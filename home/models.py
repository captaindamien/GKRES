from email.policy import default
from re import template
from tabnanny import verbose
from django.db import models
from datetime import date

from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel, InlinePanel
from wagtail.fields import RichTextField, StreamField

from wagtail.blocks import RichTextBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock

from wagtail.snippets.models import register_snippet

from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.forms import FormBuilder

from wagtailcaptcha.models import WagtailCaptchaEmailForm
from wagtailcaptcha.forms import WagtailCaptchaFormBuilder
from wagtailcaptcha.models import WagtailCaptchaForm

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
    

class Region(Orderable):
    region = ParentalKey(
        'MainPage',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='regions',
    )
    reg_id = models.CharField(
        max_length=25,
        blank=False,
        null=False,
        verbose_name='ID региона',
        help_text='ID строго по списку'
    )
    reg_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Изображение региона',
    )
    reg_link = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Ссылка',
    )
    reg_desc = RichTextField(
        verbose_name='Описание региона',
        features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'hr', 'bold', 'italic', 'link', 'superscript', 'subscript', 'strikethrough', 'blockquote'],
        help_text='Введите текст',
        blank=True,
        null=True,
    )
    ya_map = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Ссылка на Яндекс карту',
        help_text='Вставлять только src (убрать width обязательно!)'
    )


class MainPage(Page):
    subpage_types = ['HomePage']
    max_count = 1
    
    main_title = RichTextField(
        verbose_name='Заглавный текст страницы',
        features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'hr', 'bold', 'italic', 'link', 'superscript', 'subscript', 'strikethrough', 'blockquote'],
        help_text='Введите текст',
        blank=True,
        null=True,
    )
    region_title = models.CharField(
        max_length=200,
        verbose_name='Заголовок региона',
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('main_title'),
        FieldPanel('region_title'),
        MultiFieldPanel(
            [
                InlinePanel('regions'),
            ],
            heading='Добавление региона',
        ),
    ]
    
    
# Слайдер для Главной страницы
class HomeSlider(Orderable):
    slider = ParentalKey(
        'HomePage',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='slides',
    )
    caption = models.CharField(
        max_length=200,
        verbose_name='Текст слайда',
    )
    slide_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Изображение слайда',
    )
    

# Orderable группа полей для Главной страницы
class HomeService(Orderable):
    block_size = models.BooleanField(
        default=True,
        verbose_name='Большой блок?',
    )
    service = ParentalKey(
        'HomePage',
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


# Главная страница каждого сайта
class HomePage(Page):
    # определение дочерних страниц
    subpage_types = ['NewsIndexPage', 'NewsPostPage', 'ContactPage']

    # поля в бд
    about = RichTextField(
        verbose_name='О компании',
        features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'hr', 'bold','italic', 'link', 'superscript', 'subscript', 'strikethrough', 'blockquote'],
        help_text='Введите текст',
        blank=True,
        null=True,
    )
    service_title = RichTextField(
        verbose_name='Текст блока Услуги',
        features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'hr', 'bold', 'italic', 'link', 'superscript', 'subscript', 'strikethrough', 'blockquote'],
        help_text='Введите текст',
        blank=True,
        null=True,
    )
    social = RichTextField(
        features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'hr', 'bold', 'italic', 'link', 'superscript', 'subscript', 'strikethrough', 'blockquote'],
        help_text='Введите текст',
        blank=True,
        null=True,
        verbose_name = 'Социальная ответственность'
    )
    book = models.FileField(
        upload_to = 'documents/',
        blank = True,
        null = True,
        verbose_name = 'Буклет',
        help_text='Если не приложен файл буклета, слайды отображаться не будут'
    )
    ya_map = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Ссылка на Яндекс карту',
        help_text='Вставлять только src (убрать width обязательно!)'
    )

    # обьявление полей в интерфейсе администратора
    # вкладка содержимое
    content_panels = Page.content_panels + [
        FieldPanel('about'),
        FieldPanel('service_title'),
        MultiFieldPanel(
            [
                InlinePanel('services'),
            ],
            heading='Добавление услуг',
        ),
        FieldPanel('social'),
        MultiFieldPanel(
            [
                InlinePanel('slides'),
                FieldPanel('book'),
            ],
            heading='Слайды',
        ),
        FieldPanel('ya_map')
    ]


class NewsIndexPage(Page):
    # определение дочерних страниц
    subpage_types = ['NewsPostPage', 'NewsIndexPage']
    # определение родительских страниц
    parent_page_types = ['HomePage', 'NewsIndexPage']
    
    image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Изображение',
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('image'),
    ]
    
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
                features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'hr', 'br', 'bold', 'italic', 'link', 'superscript', 'subscript', 'strikethrough', 'blockquote'],
                label='Текст',
                help_text='Введите текст',
                )),
            ('documentblock', DocumentChooserBlock(label='Документ')),
            ('imgblock', ImageChooserBlock(label='Изображение', template='blocks/img_block.html')),
        ],
        # block_counts={
        #     'imgblock': {'max_num': 1},
        # },
        use_json_field=True,
        verbose_name='Добавление блоков',
    )
    created_at = models.DateField(
        verbose_name='Отображаемая дата публикации',
        default=date.today,
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('body'),
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
    

class CustomFormBuilder(WagtailCaptchaFormBuilder):
    def get_create_field_function(self, type):
        create_field_function = super().get_create_field_function(type)

        def wrapped_create_field_function(field, options):
            created_field = create_field_function(field, options)
            created_field.widget.attrs.update(
                {"placeholder": field.label},
            )

            return created_field

        return wrapped_create_field_function


class ContactPage(WagtailCaptchaEmailForm):
    form_builder = CustomFormBuilder
    
    # определение дочерних страниц
    subpage_types = []
    # определение родительских страниц
    parent_page_types = ['HomePage']
    # максимальное кол-во создаваемых страниц
    # max_count = 1
    
    landing_page_template = 'home/contact_page_landing.html',
    
    intro = RichTextField(
        verbose_name='Оглавление',
        blank=True,
    )
    thank_you_text = RichTextField(
        verbose_name='Текст после отправки',
        blank=True,
    )
    contacts = RichTextField(
        verbose_name='Место нахождения',
        features=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'hr', 'bold', 'italic', 'link', 'superscript', 'subscript', 'strikethrough', 'blockquote'],
        help_text='Введите текст',
        blank=True,
        null=True,
    )

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro'),
        InlinePanel('form_fields', label='Поле формы'),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel("subject"),
        ], heading="Настройки Email"),
        FieldPanel('contacts'),
    ]
    
    class Meta:
        verbose_name = "Страница обратной связи"
        verbose_name_plural = "Страницы обратной связи"
 
