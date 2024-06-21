from django.contrib import admin
import terno.models as models


@admin.register(models.DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'type', 'connection_str', 'enabled']
    list_filter = ['enabled', 'type']
    search_fields = ['display_name', 'type']


@admin.register(models.Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['name', 'pub_name', 'data_source']
    list_editable = ['pub_name']
    list_filter = ['data_source']
    search_fields = ['name', 'pub_name', 'data_source__display_name']


@admin.register(models.TableSelector)
class TableSelectorAdmin(admin.ModelAdmin):
    list_display = ['data_source']
    filter_horizontal = ['tables']
    list_filter = ['data_source']
    search_fields = ['data_source__display_name']


@admin.register(models.TableColumn)
class TableColumnAdmin(admin.ModelAdmin):
    list_display = ['name', 'pub_name', 'table', 'data_type']
    list_editable = ['pub_name']
    list_filter = ['table__data_source', 'table', ]
    search_fields = ['name', 'pub_name', 'table__name', 'table__data_source']


@admin.register(models.GroupTableSelector)
class GroupTableSelectorAdmin(admin.ModelAdmin):
    list_display = ['group']
    search_fields = ['group__name']
    exclude = ['exclude_tables']
    filter_horizontal = ['tables']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "tables":
            tables = models.Table.objects.exclude(public_tables__in=models.TableSelector.objects.all())
            kwargs["queryset"] = tables
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(models.GroupColumnSelector)
class GroupColumnSelectorAdmin(admin.ModelAdmin):
    list_display = ['group']
    search_fields = ['group__name']
    filter_horizontal = ['columns', 'exclude_columns']


@admin.register(models.GroupTableRowFilterSelector)
class GroupTableRowFilterSelectorAdmin(admin.ModelAdmin):
    pass
