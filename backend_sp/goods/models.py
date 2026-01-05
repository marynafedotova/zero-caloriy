from django.db import models
import uuid
from django.utils.text import slugify
from django.utils.translation import get_language
from django.urls import reverse


class TranslatableModel(models.Model):
    class Meta:
        abstract = True

    def get_i18n_field(self, field_name, fallback_lang='uk'):
        lang = get_language()[:2]
        value = getattr(self, f"{field_name}_{lang}", None)

        if value and str(value).strip():
            return value
        
        return getattr(self, f"{field_name}_{fallback_lang}", "")
    
    def get_absolute_url(self):
        return reverse('goods:product', kwargs={'product_slug': self.slug})

# Папки (Groups)
# -----------------------------
class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )
    
    order = models.IntegerField(default=0)
    is_included_in_menu = models.BooleanField(default=True)
    is_group_modifier = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=50, blank=True)
    image_links = models.JSONField(default=list, blank=True)  
    tags = models.JSONField(default=list, blank=True, null=True) 
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    seo_text = models.TextField(blank=True, null=True)
    seo_keywords = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'group'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('goods:products_by_group', kwargs={'slug': self.slug})



# -----------------------------
# Категорії страв
# -----------------------------
class ProductCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)


    class Meta:
        db_table = 'product_category'

    def __str__(self):
        return self.name

# -----------------------------
# Продукти / Страви / Модифікатори
# -----------------------------
class ProductSize(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Product(TranslatableModel):
    DISH = 'Dish'
    MODIFIER = 'Modifier'
    TYPE_CHOICES = [
        (DISH, 'Dish'),
        (MODIFIER, 'Modifier')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, blank=True)
    name_uk = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    description_uk = models.TextField(blank=True, null=True)
    description_ru = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    additional_info_uk = models.TextField(blank=True, null=True)
    additional_info_ru = models.TextField(blank=True, null=True)
    additional_info_en = models.TextField(blank=True, null=True)
    about_product_uk = models.TextField(max_length=255, blank=True, null=True)
    about_product_ru = models.TextField(max_length=255, blank=True, null=True)
    about_product_en = models.TextField(max_length=255, blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name="products")
    product_category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=DISH)
    measure_unit_uk = models.CharField(max_length=50, blank=True)
    measure_unit_ru = models.CharField(max_length=50, blank=True)
    measure_unit_en = models.CharField(max_length=50, blank=True)
    weight = models.FloatField(default=0.0)
    order = models.IntegerField(default=0, db_index=True)
    payment_subject = models.CharField(max_length=50, default="ТОВАР")
    image_url = models.URLField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    size = models.ForeignKey(ProductSize, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True, null=True, blank=True, verbose_name="Дата створення")
    updated = models.DateTimeField(auto_now=True, db_index=True, null=True, blank=True)
    is_included_in_menu = models.BooleanField(default=True)


    class Meta:
        db_table = "product"
        ordering = ["order"]

    @property
    def name(self):
        return self.get_i18n_field('name')

    @property
    def description(self):
        return self.get_i18n_field('description')
    
    @property
    def additional_info(self): # ВИПРАВЛЕНО
        return self.get_i18n_field('additional_info')

    @property
    def measure_unit(self):
        return self.get_i18n_field('measure_unit')
    
    @property
    def about_product(self):
        return self.get_i18n_field('about_product')

    def __str__(self):
        return self.name or f"Product {self.code}"

# -----------------------------
# Групи модифікаторів для продукту
# -----------------------------
class GroupModifier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="group_modifiers")
    modifier_group_name = models.CharField(max_length=255, blank=True)
    min_amount = models.IntegerField(default=0)
    max_amount = models.IntegerField(default=1)
    required = models.BooleanField(default=False)

    class Meta:
        db_table = 'group_modifier'

    def __str__(self):
        return f"{self.product.name} - {self.modifier_group_name or 'Modifier Group'}"

# -----------------------------
# Конкретні модифікатори всередині групи
# -----------------------------
class GroupModifierChild(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_modifier = models.ForeignKey(GroupModifier, on_delete=models.CASCADE, related_name="children")
    modifier = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="modifier_children")
    default_amount = models.IntegerField(default=0)
    min_amount = models.IntegerField(default=0)
    max_amount = models.IntegerField(default=0)
    required = models.BooleanField(default=False)
    hide_if_default_amount = models.BooleanField(default=False)
    splittable = models.BooleanField(default=False)
    free_of_charge_amount = models.IntegerField(default=0)

    class Meta:
        db_table = 'group_modifield_child'

    def __str__(self):
        return f"{self.group_modifier} -> {self.modifier.name}"






