from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.admin import GroupAdmin as DefaultGroupAdmin
import terno.models as models
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from allauth.account.adapter import get_adapter
from django import forms
from suggestions.tasks import generate_table_and_column_descriptions_task

admin.site.unregister(models.Group)
admin.site.unregister(models.User)


@admin.register(models.Group)
class GroupAdmin(DefaultGroupAdmin):

    def get_user_organisation(self, request):
        organisation = models.Organisation.objects.get(id=request.org_id)
        if not models.OrganisationUser.objects.filter(
                user=request.user,
                organisation=organisation).exists():
            return None
        return organisation

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if not request.user.is_superuser:
            user_organisation = self.get_user_organisation(request)

            if user_organisation:
                qs = qs.filter(organisationgroup__organisation=user_organisation)
            else:
                qs = qs.none()
        return qs

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            org_id = request.org_id
            organisation = get_object_or_404(models.Organisation, id=org_id)
            if not models.OrganisationGroup.objects.filter(organisation=organisation, group=obj).exists():
                models.OrganisationGroup.objects.create(organisation=organisation, group=obj)
        super().save_model(request, obj, form, change)


class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(
            attrs={"autofocus": True,
            "placeholder": "Enter your email"}))

    class Meta:
        model = models.User
        fields = ['email']


@admin.register(models.User)
class UserAdmin(DefaultUserAdmin):
    add_form = UserRegisterForm
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email",),
        }),
    )

    def get_user_organisation(self, request):
        organisation = models.Organisation.objects.get(id=request.org_id)
        if not models.OrganisationUser.objects.filter(
                user=request.user,
                organisation=organisation).exists():
            return None
        return organisation

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if not request.user.is_superuser:
            user_organisation = self.get_user_organisation(request)

            if user_organisation:
                qs = qs.filter(organisationuser__organisation=user_organisation)
            else:
                qs = qs.none()
        return qs

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Filter ManyToMany fields based on the user's organisation.
        """

        if not request.user.is_superuser:
            user_organisation = self.get_user_organisation(request)
            if user_organisation:
                # Filter the ManyToMany field (group) based on the organisation
                if db_field.name == 'groups':
                    kwargs["queryset"] = models.Group.objects.filter(
                        organisationgroup__organisation=user_organisation)
            else:
                kwargs["queryset"] = models.Group.objects.none()

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        user = models.User.objects.filter(email=obj.email).first()
        if user:
            obj.pk = user.pk
            for field in form.changed_data:
                setattr(user, field, getattr(obj, field))
            obj = user
        else:
            obj.username = get_adapter().generate_unique_username([obj.email])
        super().save_model(request, obj, form, change)
        org_id = request.org_id
        organisation = get_object_or_404(models.Organisation, id=org_id)
        if not models.OrganisationUser.objects.filter(organisation=organisation, user=obj).exists():
            models.OrganisationUser.objects.create(organisation=organisation, user=obj)


class OrganisationFilterMixin:
    organisation_related_field_names = []
    organisation_foreignkey_field_names = {}
    organisation_manytomany_field_names = {}

    def get_user_organisation(self, request):
        organisation = models.Organisation.objects.get(id=request.org_id)
        if not models.OrganisationUser.objects.filter(
                user=request.user,
                organisation=organisation).exists():
            return None
        return organisation

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            user_organisation = self.get_user_organisation(request)
            if user_organisation and self.organisation_related_field_names:
                # Use dynamic filtering based on the organisation field specified in the admin class
                for field_name in self.organisation_related_field_names:
                    filter_kwargs = {field_name: user_organisation}
                    qs = qs.filter(**filter_kwargs)
            else:
                qs = qs.none()
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            user_organisation = self.get_user_organisation(request)
            if user_organisation and db_field.name in self.organisation_foreignkey_field_names:
                field_filter = self.organisation_foreignkey_field_names.get(db_field.name)
                if field_filter:
                    kwargs["queryset"] = db_field.related_model.objects.filter(
                        **{field_filter: user_organisation})
            else:
                kwargs["queryset"] = db_field.related_model.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            user_organisation = self.get_user_organisation(request)
            if user_organisation and db_field.name in self.organisation_manytomany_field_names:
                field_filter = self.organisation_manytomany_field_names.get(db_field.name)
                if field_filter:
                    kwargs["queryset"] = db_field.related_model.objects.filter(
                        **{field_filter: user_organisation})
            else:
                kwargs["queryset"] = db_field.related_model.objects.none()
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class DataSourceFilter(admin.SimpleListFilter):
    title = _('Data Source')
    parameter_name = 'data_source'
    organisation_list_filter_field_names = []

    def get_user_organisation(self, request):
        organisation = models.Organisation.objects.get(id=request.org_id)
        if not models.OrganisationUser.objects.filter(user=request.user, organisation=organisation).exists():
            return None
        return organisation

    def lookups(self, request, model_admin):
        if not request.user.is_superuser:
            user_organisation = self.get_user_organisation(request)
            if user_organisation:
                return [
                    (ds.id, ds.display_name)
                    for ds in models.DataSource.objects.filter(organisationdatasource__organisation=user_organisation)
                ]
            return []
        return [(ds.id, ds.display_name) for ds in models.DataSource.objects.all()]

    def queryset(self, request, queryset):
        if not request.user.is_superuser:
            user_organisation = self.get_user_organisation(request)
            if user_organisation:
                for field_name in self.organisation_list_filter_field_names:
                    filter_kwargs = {field_name: user_organisation}
                    queryset = queryset.filter(**filter_kwargs)

        if self.value():
            queryset = queryset.filter(data_source_id=self.value())

        return queryset


@admin.register(models.LLMConfiguration)
class LLMConfigurationAdmin(OrganisationFilterMixin, admin.ModelAdmin):
    list_display = ('llm_type', 'api_key', 'model_name', 'enabled')
    organisation_related_field_names = ['organisationllm__organisation']
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
        org_id = request.org_id
        organisation = get_object_or_404(models.Organisation, id=org_id)

        if obj.enabled:
            # Disable all other configurations for the requested organisation
            models.LLMConfiguration.objects.filter(
                organisationllm__organisation=organisation,
                enabled=True
            ).update(enabled=False)

        obj.save()
        if not models.OrganisationLLM.objects.filter(organisation=organisation, llm=obj).exists():
            models.OrganisationLLM.objects.create(organisation=organisation, llm=obj)

        super().save_model(request, obj, form, change)


@admin.register(models.DataSource)
class DataSourceAdmin(OrganisationFilterMixin, admin.ModelAdmin):
    list_display = ['display_name', 'type', 'enabled', 'dialect_name', 'dialect_version', 'connection_str']
    list_filter = ['enabled', 'type']
    search_fields = ['display_name', 'type']
    organisation_related_field_names = ['organisationdatasource__organisation']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        org_id = request.org_id
        organisation = get_object_or_404(models.Organisation, id=org_id)
        if not models.OrganisationDataSource.objects.filter(organisation=organisation, datasource=obj).exists():
            models.OrganisationDataSource.objects.create(organisation=organisation, datasource=obj)
        if not models.OrganisationUser.objects.filter(organisation=organisation, user=request.user).exists():
            models.OrganisationUser.objects.create(organisation=organisation, user=request.user)


@admin.register(models.Table)
class TableAdmin(OrganisationFilterMixin, admin.ModelAdmin):
    list_display = ['name', 'public_name', 'data_source']
    list_editable = ['public_name']
    list_filter = [DataSourceFilter]
    search_fields = ['name', 'public_name', 'data_source__display_name']
    organisation_related_field_names = ['data_source__organisationdatasource__organisation']
    organisation_foreignkey_field_names = {
        'data_source' : 'organisationdatasource__organisation'
    }
    organisation_list_filter_field_names = ['data_source__organisationdatasource__organisation']
    actions = ['generate_descriptions_for_selected_tables']

    def generate_descriptions_for_selected_tables(self, request, queryset):
        """
        Admin action to enqueue a Celery task for generating table descriptions.
        """
        tables_by_datasource_org = {}

        # Group tables by (datasource_id, organisation_id)
        for table in queryset:
            data_source = table.data_source
            org_ds = models.OrganisationDataSource.objects.filter(datasource=data_source).first()
            if not org_ds:
                self.message_user(
                    request,
                    f"DataSource {data_source.id} does not have an associated organisation.",
                    level='error'
                )
                continue

            organisation = org_ds.organisation
            key = (data_source.id, organisation.id)
            if key not in tables_by_datasource_org:
                tables_by_datasource_org[key] = []
            tables_by_datasource_org[key].append(table.name)

        # Enqueue tasks for each datasource-organisation pair
        for (datasource_id, org_id), table_names in tables_by_datasource_org.items():
            generate_table_and_column_descriptions_task.delay(datasource_id, org_id, table_names)

        self.message_user(
            request,
            f"Task has been queued for {len(tables_by_datasource_org)} datasource(s).",
            level='info'
        )

    generate_descriptions_for_selected_tables.short_description = "Generate descriptions for selected tables and their columns."


@admin.register(models.PrivateTableSelector)
class PrivateTableSelectorAdmin(OrganisationFilterMixin, admin.ModelAdmin):
    list_display = ['data_source', 'private_tables_count']
    filter_horizontal = ['tables']
    search_fields = ['data_source__display_name']
    organisation_related_field_names = ['data_source__organisationdatasource__organisation']
    organisation_foreignkey_field_names = {
        'data_source': 'organisationdatasource__organisation'
    }
    organisation_manytomany_field_names = {
        'tables': 'data_source__organisationdatasource__organisation'
    }

    def private_tables_count(self, obj):
        return obj.tables.count()

    def get_list_filter(self, request):
        return super().get_list_filter(request)


@admin.register(models.TableColumn)
class TableColumnAdmin(OrganisationFilterMixin, admin.ModelAdmin):
    list_display = ['name', 'public_name', 'table', 'data_type']
    list_editable = ['public_name']
    list_filter = [DataSourceFilter]
    search_fields = ['name', 'public_name', 'table__name', 'table__data_source']
    organisation_related_field_names = ['table__data_source__organisationdatasource__organisation']
    organisation_foreignkey_field_names = {
        'table': 'data_source__organisationdatasource__organisation'
    }
    organisation_list_filter_field_names = ['table__data_source__organisationdatasource__organisation']


@admin.register(models.ForeignKey)
class ForeignKeyAdmin(OrganisationFilterMixin, admin.ModelAdmin):
    list_display = ['constrained_table', 'constrained_columns',
                    'referred_table', 'referred_columns']
    organisation_related_field_names = ['referred_schema__organisationdatasource__organisation']
    organisation_foreignkey_field_names = {
        'constrained_table': 'data_source__organisationdatasource__organisation',
        'constrained_columns': 'table__data_source__organisationdatasource__organisation',
        'referred_table': 'data_source__organisationdatasource__organisation',
        'referred_columns': 'table__data_source__organisationdatasource__organisation',
        'referred_schema': 'organisationdatasource__organisation'
    }
    # list_editable = ['public_name']
    list_filter = [DataSourceFilter]
    organisation_list_filter_field_names = [
        'referred_table__data_source__organisationdatasource__organisation'
        ]
    # search_fields = ['name', 'public_name', 'table__name', 'table__data_source']


@admin.register(models.GroupTableSelector)
class GroupTableSelectorAdmin(OrganisationFilterMixin, admin.ModelAdmin):
    list_display = ['group']
    search_fields = ['group__name']
    exclude = ['exclude_tables']
    filter_horizontal = ['tables']
    organisation_related_field_names = ['group__organisationgroup__organisation']
    organisation_foreignkey_field_names = {
        'group': 'organisationgroup__organisation'
    }
    organisation_manytomany_field_names = {
        'tables': 'data_source__organisationdatasource__organisation'
    }

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        formfield = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == "tables":
            tables = formfield.queryset.filter(
                private_tables__in=models.PrivateTableSelector.objects.all())
            formfield.queryset = tables
        return formfield


@admin.register(models.PrivateColumnSelector)
class PrivateColumnSelectorAdmin(OrganisationFilterMixin, admin.ModelAdmin):
    list_display = ['data_source', 'private_columns_count']
    filter_horizontal = ['columns']
    list_filter = [DataSourceFilter]
    search_fields = ['data_source__display_name']
    organisation_related_field_names = ['data_source__organisationdatasource__organisation']
    organisation_foreignkey_field_names = {
        'data_source': 'organisationdatasource__organisation'
    }
    organisation_manytomany_field_names = {
        'columns': 'table__data_source__organisationdatasource__organisation'
    }
    organisation_list_filter_field_names = ['data_source__organisationdatasource__organisation']
    def private_columns_count(self, obj):
        return obj.columns.count()


@admin.register(models.GroupColumnSelector)
class GroupColumnSelectorAdmin(OrganisationFilterMixin, admin.ModelAdmin):
    list_display = ['group']
    organisation_related_field_names = ['columns__table__data_source__organisationdatasource__organisation']
    search_fields = ['group__name']
    exclude = ['exclude_columns']
    filter_horizontal = ['columns', 'exclude_columns']
    organisation_foreignkey_field_names = {
        'group': 'organisationgroup__organisation'
    }
    organisation_manytomany_field_names = {
        'columns': 'table__data_source__organisationdatasource__organisation'
    }


@admin.register(models.GroupTableRowFilter)
class GroupTableRowFilterSelectorAdmin(OrganisationFilterMixin, admin.ModelAdmin):
    list_display = ['table', 'group', 'filter_str']
    organisation_related_field_names = ['table__data_source__organisationdatasource__organisation', 'group__organisationgroup__organisation']
    organisation_foreignkey_field_names = {
        'data_source': 'organisationdatasource__organisation',
        'table': 'data_source__organisationdatasource__organisation',
        'group': 'organisationgroup__organisation'
    }


@admin.register(models.TableRowFilter)
class TableRowFilterAdmin(OrganisationFilterMixin, admin.ModelAdmin):
    list_display = ['table', 'filter_str']
    organisation_related_field_names = ['table__data_source__organisationdatasource__organisation']
    organisation_foreignkey_field_names = {
        'data_source': 'organisationdatasource__organisation',
        'table': 'data_source__organisationdatasource__organisation',
        'group': 'organisationgroup__organisation'
    }


@admin.register(models.QueryHistory)
class QueryHistoryAdmin(OrganisationFilterMixin, admin.ModelAdmin):
    list_display = ['user', 'data_source', 'data_type', 'data', 'created_at']
    organisation_related_field_names = ['user__organisationuser__organisation', 'data_source__organisationdatasource__organisation']
    list_filter = [DataSourceFilter, 'data_type', 'created_at']
    search_fields = ['user__username', 'data_source__display_name', 'data']
    organisation_foreignkey_field_names = {
        'data_source': 'organisationdatasource__organisation',
        'user': 'organisationuser__organisation'
    }
    organisation_list_filter_field_names = ['data_source__organisationdatasource__organisation']


@admin.register(models.PromptLog)
class PromptLogAdmin(OrganisationFilterMixin, admin.ModelAdmin):
    list_display = ['user', 'llm_prompt', 'created_at']
    organisation_related_field_names = ['user__organisationuser__organisation']
    list_filter = ['created_at']
    search_fields = ['user__username', 'llm_prompt']
    organisation_foreignkey_field_names = {
        'user': 'organisationuser__organisation'
    }


@admin.register(models.SystemPrompts)
class SystemPromptsAdmin(OrganisationFilterMixin, admin.ModelAdmin):
    list_display = ['data_source', 'system_prompt']
    organisation_related_field_names = ['data_source__organisationdatasource__organisation']
    list_filter = [DataSourceFilter]
    search_fields = ['data_source__display_name', 'system_prompt']
    organisation_foreignkey_field_names = {
        'data_source': 'organisationdatasource__organisation',
    }
    organisation_list_filter_field_names = ['data_source__organisationdatasource__organisation']
