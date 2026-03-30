from django.contrib import admin

from blog.models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = ('title_uk', 'author', 'created_at', 'is_published')
    list_filter = ('is_published', 'author', 'created_at')
    search_fields = ('title_uk', 'title_en', 'title_ru')
    prepopulated_fields = {'slug': ('title_uk',)}

    fieldsets = (
        ('Загальна інформація', {
            'fields': ('image', 'author', 'created_at', 'slug', 'is_published')
        }),
        ('Українська версія (UK)', {
            'fields': ('title_uk', 'text_uk', 'quote_uk'),
        }),
        ('English Version (EN)', {
            'fields': ('title_en', 'text_en', 'quote_ru'),
            'classes': ('collapse',), 
        }),
        ('Русская версия (RU)', {
            'fields': ('title_ru', 'text_ru', 'quote_en'),
            'classes': ('collapse',),
        }),
    )