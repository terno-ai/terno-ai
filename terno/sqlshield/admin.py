from django.contrib import admin

from . import models

# Register your models here.

class DataSourceAdmin(admin.ModelAdmin):
    pass

class TableSelectorAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.DataSource, DataSourceAdmin)

admin.site.register(models.TableSelector, TableSelectorAdmin)
