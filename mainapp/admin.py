from django.contrib import admin
from .models import User, Customer, Package

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    search_fields = ('username', 'email')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'id_number')
    search_fields = ('first_name', 'last_name', 'id_number')

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'speed', 'price', 'sector')
    search_fields = ('name', 'sector')
