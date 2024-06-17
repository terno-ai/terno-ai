from django.contrib import admin
from . import models


@admin.register(models.DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TableSelector)
class TableSelectorAdmin(admin.ModelAdmin):
    pass
