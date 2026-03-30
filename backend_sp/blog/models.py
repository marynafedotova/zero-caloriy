from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import get_language

from ckeditor.fields import RichTextField

class TranslatableModel(models.Model):
    class Meta:
        abstract = True

    def get_i18n_field(self, field_name, fallback_lang='uk'):
        lang = get_language()[:2]
        value = getattr(self, f"{field_name}_{lang}", None)

        if value and str(value).strip():
            return value
        
        return getattr(self, f"{field_name}_{fallback_lang}", "")

class Post(TranslatableModel): 
    image = models.ImageField(
        upload_to='blog/images/', 
        verbose_name="Зображення"
    )
    # Додаємо slug для get_absolute_url
    slug = models.SlugField(
        max_length=255, 
        unique=True, 
        verbose_name="URL-адреса (slug)"
    )
    created_at = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Дата створення"
    )
    author = models.CharField(
        max_length=100, 
        default="Зеро калорій", 
        verbose_name="Автор"
    )
    is_published = models.BooleanField(
        default=True, 
        verbose_name="Опубліковано"
    )
    # --- ПЕРЕКЛАДИ: НАЗВА ---
    title_uk = models.CharField(max_length=255, verbose_name="Назва (УКР)")
    title_en = models.CharField(max_length=255, verbose_name="Назва (ENG)", blank=True, null=True)
    title_ru = models.CharField(max_length=255, verbose_name="Назва (РУС)", blank=True, null=True)

    # --- ПЕРЕКЛАДИ: ТЕКСТ в символі ---
    quote_uk = models.TextField(verbose_name="Текст цитата (УКР)", blank=True, null=True)
    quote_en = models.TextField(verbose_name="Текст цитата (ENG)", blank=True, null=True)
    quote_ru = models.TextField(verbose_name="Текст цитата (РУС)", blank=True, null=True)

    # --- ПЕРЕКЛАДИ: ТЕКСТ ---
    text_uk = RichTextField(verbose_name="Текст (УКР)")
    text_en = RichTextField(verbose_name="Текст (ENG)", blank=True, null=True)
    text_ru = RichTextField(verbose_name="Текст (РУС)", blank=True, null=True)

    class Meta:
        verbose_name = "Стаття"
        verbose_name_plural = "Статті"
        ordering = ['-created_at']

    @property
    def title(self):
        return self.get_i18n_field('title')

    @property
    def text(self):
        return self.get_i18n_field('text')

    @property
    def quote(self):
        return self.get_i18n_field('quote')


    def get_absolute_url(self):
        return reverse('blog:post', kwargs={'post_slug': self.slug})