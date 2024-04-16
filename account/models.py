import os
from os.path import splitext
import shutil

from django.conf import settings
from django.db import models
from django import forms
from django.shortcuts import redirect, render
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect

from wagtail.models import Page, Orderable, Collection
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField, FORM_FIELD_CHOICES
from wagtail.contrib.forms.views import SubmissionsListView
from wagtail.contrib.forms.forms import FormBuilder
from modelcluster.fields import ParentalKey
from wagtail.documents import get_document_model
from wagtail.images.fields import WagtailImageField
from wagtail.images import get_image_model

from .worksheet_funcs import main


class AccountPage(Page):
    parent_page_types = ['wagtailcore.Page']
    
    welcome_text = models.CharField(
        max_length=100,
        verbose_name='Встречающий текст страницы',
        blank=True,
        null=True,
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('welcome_text'),
        MultiFieldPanel(
            [
                InlinePanel('services'),
            ],
            heading='Добавление пунктов',
        ),
    ]
    
    def serve(self, request):
        if request.user.is_authenticated:
           return super().serve(request)
        else:
           return redirect('/admin/login/?next=/')
       

class AccountServices(Orderable):
    block_size = models.BooleanField(
        default=True,
        verbose_name='Большой блок?',
    )
    service = ParentalKey(
        'AccountPage',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='services',
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название услуги',
    )
    icon = models.CharField(
        max_length=50,
        verbose_name='Название иконки',
        help_text='Можно вставлять fa-fa и micons',
        blank=True,
        null=True,
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Изображение',
    )
    link = models.CharField(
        max_length=200,
        verbose_name='Ссылка',
    )
    is_menu = models.BooleanField(
        default=True,
        verbose_name='Показывать в меню?',
    )


class WorksheetFormField(AbstractFormField):
    # Добавление полей в форму в админке
    CHOICES = list(FORM_FIELD_CHOICES) + \
        [('image', 'Изображение')] + \
        [('document', 'Документ')]

    field_type = models.CharField(
        verbose_name='field type',
        max_length=16,
        choices=CHOICES
    )
    page = ParentalKey(
        'WorksheetPage',
        on_delete=models.CASCADE,
        related_name='form_fields'
    )


class WorksheetFormBuilder(FormBuilder):
    # Ожидает формат create_<image_name>_field -> Имя берется из CHOICES
    def create_image_field(self, field, options):
        return WagtailImageField(**options)
    
    def create_document_field(self, field, options):
        return forms.FileField(**options)
    
    def get_create_field_function(self, type):
        create_field_function = super().get_create_field_function(type)

        def wrapped_create_field_function(field, options):
            created_field = create_field_function(field, options)
            created_field.widget.attrs.update(
                {"placeholder": field.label},
            )

            return created_field

        return wrapped_create_field_function


class WorksheetSubmissionsListView(SubmissionsListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.is_export:
            # generate a list of field types, the first being the injected 'submission date'
            field_types = ['submission_date'] + [field.field_type for field in self.form_page.get_form_fields()]
            data_rows = context['data_rows']

            ImageModel = get_image_model()

            for data_row in data_rows:
                fields = data_row['fields']

                for idx, (value, field_type) in enumerate(zip(fields, field_types)):
                    if field_type == 'image' and value:
                        image = ImageModel.objects.get(pk=value)
                        rendition = image.get_rendition('fill-100x75|jpegquality-40')
                        preview_url = rendition.url
                        url = reverse('wagtailimages:edit', args=(image.id,))

                        fields[idx] = format_html(
                            "<a href='{}'><img alt='Uploaded image - {}' src='{}' />{} ({})</a>",
                            url,
                            image.title,
                            preview_url,
                            image.title,
                            value
                        )

        return context


class WorksheetPage(AbstractEmailForm):  
    form_builder = WorksheetFormBuilder
    submissions_list_view_class = WorksheetSubmissionsListView
    
    parent_page_types = [AccountPage]
    max_count = 1
    
    template = 'account/worksheet_page.html'
    landing_page_template = 'account/worksheet_page_landing.html'
    
    uploaded_image_collection = models.ForeignKey(
        'wagtailcore.Collection',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    content_panels = AbstractEmailForm.content_panels + [
        InlinePanel('form_fields', label="Form fields"),
    ]
    
    settings_panels = AbstractEmailForm.settings_panels + [
        FieldPanel('uploaded_image_collection')
    ]
    
    def serve(self, request):
        if request.user.is_authenticated:
            if request.method == 'POST':
                form = self.get_form(request.POST, request.FILES, page=self, user=request.user)
                
                if form.is_valid():
                    response = self.process_form_submission(form)
                    if isinstance(response, HttpResponseRedirect):
                        return response  # Обработка редиректа
                    else:
                        return redirect(self.get_success_url())
            else:
                form = self.get_form(page=self, user=request.user)
            
            context = self.get_context(request)
            context['form'] = form
            
            return render(request, self.template, context)
        else:
           return redirect('/admin/login/?next=/')
    
    def get_uploaded_image_collection(self):
        collection = self.uploaded_image_collection
        return collection or Collection.get_first_root_node()
    
    @staticmethod
    def get_image_title(filename):
        if filename:
            result = splitext(filename)[0]
            result = result.replace('-', ' ').replace('_', ' ')
            return result.title()
        return ''

    def process_form_submission(self, form):
        cleaned_data = form.cleaned_data
        
        for name, field in form.fields.items():
            if isinstance(field, WagtailImageField):
                image_file_data = cleaned_data[name]
                if image_file_data:
                    ImageModel = get_image_model()

                    kwargs = {
                        'file': cleaned_data[name],
                        'title': self.get_image_title(cleaned_data[name].name),
                        'collection': self.get_uploaded_image_collection(),
                    }

                    if form.user and not form.user.is_anonymous:
                        kwargs['uploaded_by_user'] = form.user

                    image = ImageModel(**kwargs)
                    image.save()

                    final_image_name = image.file.name
                    cleaned_data.update({name: final_image_name})
                else:
                    # remove the value from the data
                    del cleaned_data[name]
            elif isinstance(field, forms.FileField):
                document_file_data = cleaned_data[name]
                if document_file_data:
                    DocumentModel = get_document_model()

                    kwargs = {
                        'file': cleaned_data[name],
                        'title': self.get_image_title(cleaned_data[name].name),
                        'collection': self.get_uploaded_image_collection()
                    }

                    if form.user and not form.user.is_anonymous:
                        kwargs['uploaded_by_user'] = form.user

                    document = DocumentModel(**kwargs)
                    document.save()
                    
                    final_document_name = document.file.name
                    cleaned_data.update({name: final_document_name})
                    
                    # данные для worksheet_funcs.main
                    form_data = {}
                    data_list = [v for v in cleaned_data.values()]
                    
                    form_data['file_name'] = data_list[0]
                    form_data['sheet_name'] = data_list[1]
                    form_data['month'] = data_list[2]
                    form_data['month_part'] = data_list[3]
                    form_data['year'] = data_list[4]
                    form_data['date_row'] = data_list[5]
                    form_data['employee_col'] = data_list[6]
                    
                    chief_name = form.user.first_name.split(' ')
                    try:
                        form_data['chief'] = f'{form.user.last_name} {chief_name[0][0]}.{chief_name[1][0]}.'
                    except IndexError:
                        form_data['chief'] = f'{form.user.last_name} {form.user.first_name[0]}.'

                    file_exts = ('xlsx', 'xls', 'xlsm')
                    if form_data['file_name'].endswith(file_exts):
                        # Запуск скрипта, который будет выполняться при отправке формы       
                        main(form_data=form_data)
                        
                        # Создание архива и перемещение его в нужную директорию
                        worksheet_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'worksheet_docs')
                        dir_to_archive = os.path.join(worksheet_dir, 'raw_files')
                        archive_name = f"docs-{final_document_name.split('/')[1]}.zip"
                        archive_relative_path = os.path.join("documents", archive_name)
                        archive_full_path = os.path.join(settings.MEDIA_ROOT, archive_relative_path)
                        shutil.make_archive(archive_full_path.replace('.zip', ''), 'zip', dir_to_archive)

                        # Получаем или создаем коллекцию
                        word_files_collection, created = Collection.objects.get_or_create(
                            name='word_docs',
                            defaults={'name': 'word_docs'},
                        )
                        
                        DocumentModel = get_document_model()
                        document = DocumentModel(
                            title=archive_name,
                            file=archive_relative_path,
                            collection=word_files_collection,
                        )

                        document.save()
                        
                        # Удаляем файлы из папки raw_docs
                        shutil.rmtree(dir_to_archive, ignore_errors=True)
                        
                        archive_url = document.file.url
                        return HttpResponseRedirect(archive_url)
                else:
                    del cleaned_data[name]
        
        submission = self.get_submission_class().objects.create(
            form_data=form.cleaned_data,
            page=self,
        )

        if self.to_address:
           self.send_mail(form)

        return submission    
