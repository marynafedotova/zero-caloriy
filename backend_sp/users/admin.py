from django.contrib import admin
from users.models import User

@admin.register(User)
class UsertAdmin(admin.ModelAdmin):
    list_display = ('first_name',)
   
