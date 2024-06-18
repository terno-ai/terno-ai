from django.contrib import admin
from . import models


@admin.register(models.DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    pass


# @admin.register(models.TableSelector)
# class TableSelectorAdmin(admin.ModelAdmin):
#     pass


@admin.register(models.Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['name', 'pub_name', 'data_source']


@admin.register(models.TableColumn)
class TableColumnAdmin(admin.ModelAdmin):
    list_display = ['name', 'pub_name', 'table', 'data_type']


@admin.register(models.GroupTableSelector)
class GroupTableSelectorAdmin(admin.ModelAdmin):
    list_display = ['group']
    filter_horizontal = ['tables', 'exclude_tables']


@admin.register(models.GroupColumnSelector)
class GroupColumnSelectorAdmin(admin.ModelAdmin):
    filter_horizontal = ['columns', 'exclude_columns']


@admin.register(models.GroupTableRowFilterSelector)
class GroupTableRowFilterSelectorAdmin(admin.ModelAdmin):
    pass
