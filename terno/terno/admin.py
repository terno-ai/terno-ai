from django.contrib import admin
import terno.models as models


@admin.register(models.LLMConfiguration)
class LLMConfigurationAdmin(admin.ModelAdmin):
    list_display = ('llm_type', 'api_key', 'model_name', 'enabled')
    search_fields = ('llm_type', 'model_name')
    fieldsets = (
        ('Basic Configuration', {
            'fields': ('llm_type', 'api_key', 'enabled'),
        }),
        ('Advanced Configuration (Optional)', {
            'classes': ('collapse',),
            'fields': ('model_name', 'temperature', 'custom_system_message',
                       'max_tokens', 'top_p', 'top_k', 'custom_parameters'),
            'description': 'Optional Fields: These fields are optional.'
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.enabled:
            # Disable all other configurations
            models.LLMConfiguration.objects.filter(enabled=True).update(enabled=False)
        super().save_model(request, obj, form, change)


@admin.register(models.DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'type', 'connection_str', 'enabled']
    list_filter = ['enabled', 'type']
    search_fields = ['display_name', 'type']


@admin.register(models.Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['name', 'public_name', 'data_source']
    list_editable = ['public_name']
    list_filter = ['data_source']
    search_fields = ['name', 'public_name', 'data_source__display_name']


@admin.register(models.PrivateTableSelector)
class PrivateTableSelectorAdmin(admin.ModelAdmin):
    list_display = ['data_source', 'private_tables_count']
    filter_horizontal = ['tables']
    list_filter = ['data_source']
    search_fields = ['data_source__display_name']

    def private_tables_count(self, obj):
        return obj.tables.count()


@admin.register(models.TableColumn)
class TableColumnAdmin(admin.ModelAdmin):
    list_display = ['name', 'public_name', 'table', 'data_type']
    list_editable = ['public_name']
    list_filter = ['table__data_source', 'table']
    search_fields = ['name', 'public_name', 'table__name', 'table__data_source']


@admin.register(models.GroupTableSelector)
class GroupTableSelectorAdmin(admin.ModelAdmin):
    list_display = ['group']
    search_fields = ['group__name']
    exclude = ['exclude_tables']
    filter_horizontal = ['tables']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "tables":
            tables = models.Table.objects.filter(
                private_tables__in=models.PrivateTableSelector.objects.all())
            kwargs["queryset"] = tables
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(models.PrivateColumnSelector)
class PrivateColumnSelectorAdmin(admin.ModelAdmin):
    list_display = ['data_source', 'private_columns_count']
    filter_horizontal = ['columns']
    list_filter = ['data_source']
    search_fields = ['data_source__display_name']

    def private_columns_count(self, obj):
        return obj.columns.count()

@admin.register(models.GroupColumnSelector)
class GroupColumnSelectorAdmin(admin.ModelAdmin):
    list_display = ['group']
    search_fields = ['group__name']
    exclude = ['exclude_columns']
    filter_horizontal = ['columns', 'exclude_columns']


@admin.register(models.GroupTableRowFilter)
class GroupTableRowFilterSelectorAdmin(admin.ModelAdmin):
    list_display = ['table', 'group', 'filter_str']


@admin.register(models.TableRowFilter)
class TableRowFilterAdmin(admin.ModelAdmin):
    list_display = ['table', 'filter_str']


@admin.register(models.QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'data_source', 'data_type', 'data', 'created_at']
    list_filter = ['data_source', 'data_type', 'created_at']
