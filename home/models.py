from email.policy import default
import imp
from re import template
from tabnanny import verbose
from django.db import models
from datetime import date

from wagtail.models import Page, Orderable
from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, StreamFieldPanel, MultiFieldPanel, InlinePanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.core.fields import RichTextField, StreamField

from wagtail.core.blocks import RichTextBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock

from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.forms import FormBuilder

from modelcluster.fields import ParentalKey

from slugify import slugify


@register_snippet
class Footer(models.Model):
    title = models.CharField(
        verbose_name='Название',
        max_length=100,
        blank=True,
        null=True,
    )
    bodytext = RichTextField(
        verbose_name='Текст футера',
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('bodytext'),
    ]

    class Meta:
        verbose_name = "Футер"
        verbose_name_plural = "Футеры"
    
    def __str__(self):
        return self.title


@register_snippet
class Contacts(models.Model):
    employee_post = models.CharField(
        verbose_name='Должность',
        max_length=100,
        blank=True,
        null=True,
    )
    employee_fullname = models.CharField(
        verbose_name='ФИО',
        max_length=100,
        blank=True,
        null=True,
    )
    employee_contact = models.EmailField(
        verbose_name='адрес эл. почты',
        max_length=100,
        blank=True,
        null=True,
    )

    panels = [
        FieldPanel('employee_post'),
        FieldPanel('employee_fullname'),
        FieldPanel('employee_contact'),
    ]

    class Meta:
        verbose_name = "Контакты"
        verbose_name_plural = "Контакты"
    
    def __str__(self):
        return self.employee_fullname


class HomePage(Page):
    # определение дочерних страниц
    subpage_types = ['NewsIndexPage', 'NewsPostPage', 'ContactPage']
    # максимальное кол-во создаваемых страниц
    max_count = 2

    # поля в бд
    about = RichTextField(
        verbose_name='О компании',
        features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'hr', 'bold','italic', 'link', 'superscript', 'subscript', 'strikethrough', 'blockquote'],
        help_text='Введите текст',
        blank=True,
        null=True,
    )
    service = RichTextField(
        verbose_name='Услуги',
        features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'hr', 'bold', 'italic', 'link', 'superscript', 'subscript', 'strikethrough', 'blockquote'],
        help_text='Введите текст',
        blank=True,
        null=True,
    )
    social = RichTextField(
        verbose_name='Социальная ответственность',
        features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'hr', 'bold', 'italic', 'link', 'superscript', 'subscript', 'strikethrough', 'blockquote'],
        help_text='Введите текст',
        blank=True,
        null=True,
    )
    org_office = RichTextField(
        verbose_name='Место нахождения',
        features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'hr', 'bold', 'italic', 'link', 'superscript', 'subscript', 'strikethrough', 'blockquote'],
        help_text='Введите текст',
        blank=True,
        null=True,
    )
    org_email = RichTextField(
        verbose_name='Адреса эл. почты',
        features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'hr', 'bold', 'italic', 'link', 'superscript', 'subscript', 'strikethrough', 'blockquote'],
        help_text='Введите текст',
        blank=True,
        null=True,
    )
    org_phone = RichTextField(
        verbose_name='Номера телефонов',
        features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'hr', 'bold', 'italic', 'link', 'superscript', 'subscript', 'strikethrough', 'blockquote'],
        help_text='Введите текст',
        blank=True,
        null=True,
    )

    # обьявление полей в интерфейсе администратора
    # вкладка содержимое
    content_panels = Page.content_panels + [
        FieldPanel('about'),
        FieldPanel('service'),
        FieldPanel('social'),
        FieldPanel('org_office'),
        FieldPanel('org_email'),
        FieldPanel('org_phone'),
    ]


class NewsIndexPage(Page):
    # определение дочерних страниц
    subpage_types = ['NewsPostPage', 'NewsIndexPage']
    # определение родительских страниц
    parent_page_types = ['HomePage', 'NewsIndexPage']
    
    class Meta:
        verbose_name = "Страница категории"
        verbose_name_plural = "Страницы категории"
        
        
class NewsPostPage(Page):
    # определение дочерних страниц
    subpage_types = []
    # определение родительских страниц
    parent_page_types = ['HomePage', 'NewsIndexPage']
    
    body = StreamField(
        [
            ('rtfblock', RichTextBlock(
                features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'hr', 'bold', 'italic', 'link', 'superscript', 'subscript', 'strikethrough', 'blockquote'],
                label='Текст',
                help_text='Введите текст',
                )),
            ('documentblock', DocumentChooserBlock(label='Документ')),
            ('imgblock', ImageChooserBlock(label='Изображение', template='blocks/img_block.html')),
        ],
        block_counts={
            'rtfblock': {'min_num': 1},
            'imgblock': {'max_num': 1},
        },
        verbose_name='Добавление блоков',
    )
    created_at = models.DateField(
        verbose_name='Отображаемая дата публикации',
        default=date.today,
    )
    
    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]
    promote_panels = Page.promote_panels + [
        FieldPanel('created_at'),
    ]
    
    class Meta:
        verbose_name = "Новостная страница"
        verbose_name_plural = "Новостные страницы"
    
    def full_clean(self, *args, **kwargs):
        super(NewsPostPage, self).full_clean(*args, **kwargs)

        if self.slug:
            self.slug = slugify(self.slug)
            

class FormField(AbstractFormField):
    page = ParentalKey(
        'ContactPage',
        on_delete=models.CASCADE,
        related_name='form_fields',
    )
    

class CustomFormBuilder(FormBuilder):
    def get_create_field_function(self, type):
        create_field_function = super().get_create_field_function(type)

        def wrapped_create_field_function(field, options):
            created_field = create_field_function(field, options)
            created_field.widget.attrs.update(
                {"placeholder": field.label},
            )

            return created_field

        return wrapped_create_field_function


class ContactPage(AbstractEmailForm):
    form_builder = CustomFormBuilder
    
    # определение дочерних страниц
    subpage_types = []
    # определение родительских страниц
    parent_page_types = ['HomePage']
    # максимальное кол-во создаваемых страниц
    max_count = 1
    
    
    landing_page_template = 'home/contact_page_landing.html',
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro'),
        InlinePanel('form_fields', label='Form Fields'),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel("subject"),
        ], heading="Email Settings"),
    ]
    
    class Meta:
        verbose_name = "Страница обратной связи"
        verbose_name_plural = "Страницы обратной связи"
 