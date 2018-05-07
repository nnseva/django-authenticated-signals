from django.contrib import admin

from testapp.models import *

class ChildAdmin(admin.TabularInline):
    model = SomeChild

# Register your models here.
class ObjectAdmin(admin.ModelAdmin):
    inlines = [
        ChildAdmin,
    ]

# Register your models here.
admin.site.register(SomeObject,ObjectAdmin)
