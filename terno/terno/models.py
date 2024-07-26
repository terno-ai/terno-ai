from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
import json
from django.core.exceptions import ValidationError
from django.utils import timezone


class LLMConfiguration(models.Model):
    LLM_TYPES = [
        ('openai', 'OpenAI'),
        ('gemini', 'Gemini'),
        ('anthropic', 'Anthropic'),
        ('custom', 'CustomLLM')
        # Add other LLM types here
    ]

    llm_type = models.CharField(
        max_length=64, choices=LLM_TYPES,
        help_text="Select the type of LLM (e.g., OpenAI, Gemini, etc.).")
    api_key = models.CharField(
        max_length=512,
        help_text="Enter the API key for accessing the LLM service.")
    model_name = models.CharField(
        max_length=256, blank=True, null=True,
        help_text="Specify the model name to use (leave blank for default).")
    temperature = models.FloatField(
        blank=True, null=True,
        help_text="Set the sampling temperature where higher \
            values make output more random (leave blank for default).")
    custom_system_message = models.TextField(
        blank=True, null=True,
        help_text="Optional system message to set the behavior \
            of the assistant (leave blank for default)")
    max_tokens = models.IntegerField(
        blank=True, null=True,
        help_text="Specify the maximum number of tokens to \
            generate (leave blank for default).")
    top_p = models.FloatField(
        blank=True, null=True,
        help_text="Set the top-p sampling value (controls diversity \
            via nucleus sampling). Leave blank for default.")
    top_k = models.FloatField(
        blank=True, null=True,
        help_text="Set the top-k parameter value (Limits the model \
            to consider only the top k most probable next words). \
            Leave blank for default.")
    enabled = models.BooleanField(
        default=True,
        help_text="Make sure to enable only one LLM at a time.")
    custom_parameters = models.JSONField(
        blank=True, null=True,
        help_text=(
            "Enter parameters as a JSON object. Use this field if you \
            want to pass additional paramters than the one defined above. \
            These parameters will be passed when invoking the LLM. "
            "Example: {\"param1\": value1, \"param2\": value2, ... and \
            so on }. In case of string values, enclose it in either \
            single or double quotes."
            "Note: Only include parameters that are supported by the LLM \
            you are using, otherwise an error may occur."
        ))

    def clean(self):
        super().clean()
        if self.custom_parameters:
            try:
                parameters_dict = json.loads(json.dumps(self.custom_parameters))
                if not isinstance(parameters_dict, dict):
                    raise ValidationError("Parameters must be a JSON object containing key-value pairs.")
            except (ValueError, TypeError) as e:
                raise ValidationError(f"Invalid JSON format: {e}")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.llm_type} - {self.model_name or 'default-model'}"


class DataSource(models.Model):
    class DBType(models.TextChoices):
        default = "generic", _("Generic")
        Oracle = "oracle", _("Oracle")
        MSSQL = "mysql", _("MySQL")
        postgres = "postgres", _("Postgres")
    display_name = models.CharField(max_length=20, default='Datasource 1')
    type = models.CharField(max_length=20, choices=DBType,
                            default=DBType.default)
    connection_str = models.TextField(
        max_length=300, help_text="Connection string for the datasource")
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name


class Table(models.Model):
    """Model to represent a table in the data source."""
    name = models.CharField(max_length=255)
    public_name = models.CharField(max_length=255, null=True, blank=True)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    description = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return f"{self.data_source.display_name} - {self.name}"

    def get_table_name(self):
        return self.public_name if self.public_name else self.name


class TableColumn(models.Model):
    """Model to represent a column in a table."""
    name = models.CharField(max_length=255)
    public_name = models.CharField(max_length=255, null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    data_type = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.table} - {self.name}"

    def get_column_name(self):
        return self.public_name if self.public_name else self.name


class PrivateTableSelector(models.Model):
    """Model for user to select private tables."""
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    tables = models.ManyToManyField(Table, blank=True,
                                    related_name='private_tables')

    def __str__(self):
        return f'{self.data_source}'


class GroupTableSelector(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    tables = models.ManyToManyField(Table, blank=True,
                                    related_name='include_tables')
    exclude_tables = models.ManyToManyField(Table, blank=True,
                                            related_name='exclude_tables')

    def __str__(self) -> str:
        return f'{self.group.name}'

    def get_pub_table(self):
        tables_items = self.tables.all()
        exclude_tables_items = self.exclude_tables.all()
        diff = tables_items.difference(exclude_tables_items)
        return diff


class PrivateColumnSelector(models.Model):
    """Model for user to select private columns."""
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    columns = models.ManyToManyField(TableColumn, blank=True,
                                     related_name='private_columns')

    def __str__(self):
        return f'{self.data_source}'


class GroupColumnSelector(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    columns = models.ManyToManyField(TableColumn, blank=True,
                                     related_name='include_columns')
    exclude_columns = models.ManyToManyField(TableColumn, blank=True,
                                             related_name='exclude_columns')

    def __str__(self) -> str:
        return f'{self.group.name}'

    def get_pub_column(self):
        columns_items = self.columns.all()
        exclude_columns_items = self.exclude_columns.all()
        diff = columns_items.difference(exclude_columns_items)
        return diff


class GroupTableRowFilter(models.Model):
    # TODO: Unique on datasource, table and role
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    filter_str = models.CharField(max_length=300)


class TableRowFilter(models.Model):
    # TODO: Unique on datasource and table
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    filter_str = models.CharField(max_length=300)


class QueryHistory(models.Model):
    DATA_TYPES = [
        ('user_prompt', 'User Prompt'),
        ('generated_sql', 'Generated SQL'),
        ('executed_sql', 'Executed SQL'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    data_type = models.CharField(
        max_length=64, choices=DATA_TYPES,
        help_text="Select the type of data you want to save")
    data = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
