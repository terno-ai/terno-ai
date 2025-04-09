from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
import json
from django.core.exceptions import ValidationError
from subscription.models import LLMCredit


class LLMConfiguration(models.Model):
    LLM_TYPES = [
        ('openai', 'OpenAI'),
        ('gemini', 'Gemini'),
        ('anthropic', 'Anthropic'),
        ('ollama', 'Ollama'),
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
            want to pass additional parameters than the one defined above. \
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
        bigquery = "bigquery", _("BigQuery")
    display_name = models.CharField(max_length=20, default='Datasource 1')
    type = models.CharField(max_length=20, choices=DBType,
                            default=DBType.default)
    connection_str = models.TextField(
        max_length=300, help_text="Connection string for the datasource")
    connection_json = models.JSONField(
        null=True, blank=True,
        help_text="JSON key file contents for authentication")
    description = models.TextField(
        max_length=1024, null=True, blank=True, default='',
        help_text="Give description of your datasource/schema.")
    enabled = models.BooleanField(default=True)
    dialect_name = models.CharField(
        max_length=20, null=True, blank=True, default='',
        help_text="Auto-generated on save")
    dialect_version = models.CharField(
        max_length=20, null=True, blank=True, default='',
        help_text="Auto-generated on save")

    def __str__(self):
        return self.display_name


class Table(models.Model):
    """Model to represent a table in the data source."""
    name = models.CharField(max_length=255)
    public_name = models.CharField(max_length=255, null=True, blank=True)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    description = models.CharField(max_length=300, null=True, blank=True)
    sample_rows = models.JSONField(null=True, blank=True)
    description_updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.data_source.display_name} - {self.name}"


class TableColumn(models.Model):
    """Model to represent a column in a table."""
    name = models.CharField(max_length=255)
    public_name = models.CharField(max_length=255, null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    data_type = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=300, null=True, blank=True)
    unique_categories = models.JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        return f"{self.table} - {self.name}"


class ForeignKey(models.Model):
    constrained_table = models.ForeignKey(Table,
                                          on_delete=models.CASCADE,
                                          related_name='contrained_table',
                                          null=True, blank=True)
    constrained_columns = models.ForeignKey(TableColumn,
                                            on_delete=models.CASCADE,
                                            related_name='contrained_columns')
    referred_table = models.ForeignKey(Table, on_delete=models.CASCADE,
                                       related_name='referred_table')
    referred_columns = models.ForeignKey(TableColumn, on_delete=models.CASCADE,
                                         related_name='referred_columns')
    referred_schema = models.ForeignKey(DataSource, on_delete=models.CASCADE,
                                        null=True, blank=True)


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


class Organisation(models.Model):
    name = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='organisation')
    logo = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    llm_credit = models.ForeignKey(LLMCredit, null=True, blank=True,
                                   on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Automatically create OrganisationUser for the owner
        if not OrganisationUser.objects.filter(
                organisation=self, user=self.owner).exists():
            OrganisationUser.objects.create(organisation=self, user=self.owner)

        # Grant staff status to the owner user if not already staff
        if not self.owner.is_staff:
            self.owner.is_staff = True
            self.owner.save()

        # Assign org_owner group to org owner
        org_owner_group = Group.objects.filter(name='org_owner').first()
        self.owner.groups.add(org_owner_group)
        self.owner.save()


class OrganisationLLM(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    llm = models.ForeignKey(LLMConfiguration, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


class OrganisationUser(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['organisation', 'user'], name='user_organisation')
        ]


class OrganisationGroup(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


class OrganisationDataSource(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    datasource = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


class QueryHistory(models.Model):
    DATA_TYPES = [
        ('user_prompt', 'User Prompt'),
        ('generated_sql', 'Generated SQL'),
        ('user_executed_sql', 'User Executed SQL'),
        ('actual_executed_sql', 'Actual Executed SQL')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    data_type = models.CharField(
        max_length=64, choices=DATA_TYPES,
        help_text="Select the type of data you want to save")
    data = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


class PromptLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    llm_prompt = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


class SystemPrompts(models.Model):
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    system_prompt = models.TextField(blank=True, null=True)


class DatasourceSuggestions(models.Model):
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    suggestion = models.TextField(blank=True, null=True)


class Conversation(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE,
                                     related_name='conversations')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='conversations')
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title or f"Conversation {self.pk}"


class Chat(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('agent', 'Agent'),
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE,
                                     related_name='chats')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL,
                               null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.role}] {self.content[:30]}..."


class AgentStep(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('error', 'Error'),
    )

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE,
                             related_name='agent_steps')
    step_number = models.PositiveIntegerField()
    thought = models.TextField()
    action_type = models.CharField(max_length=100)
    action_input = models.TextField(blank=True)
    result = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chat', 'step_number')
        ordering = ['step_number']

    def __str__(self):
        return f"Step {self.step_number} - {self.action_type}"


class Artifact(models.Model):
    step = models.ForeignKey(AgentStep, on_delete=models.CASCADE,
                             related_name='artifacts')
    file = models.FileField(upload_to='artifacts/')
    name = models.CharField(max_length=255)
    artifact_type = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.file.name
