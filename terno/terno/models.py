from django.db import models
from django.utils.translation import gettext_lazy as _


class DataSource(models.Model):
    class DBType(models.TextChoices):
        default = "generic", _("Generic")
        Oracle = "oracle", _("Oracle")
        MSSQL = "mysql", _("MySQL")
        postgres = "postgres", _("Postgres")
    type = models.CharField(max_length=20,
                            choices=DBType,
                            default=DBType.default
                            )
    connection_str = models.CharField(max_length=300)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.connection_str


class Table(models.Model):
    """Model to represent a table in the data source."""
    name = models.CharField(max_length=255)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.data_source.name} - {self.name}"


class TableColumn(models.Model):
    """Model to represent a column in a table."""
    name = models.CharField(max_length=255)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    data_type = models.CharField(max_length=50, blank=True)  # Optional field for data type

    def __str__(self):
        return f"{self.table} - {self.name}"


class TableSelector(models.Model):
    """Model for user to select tables."""
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    tables = models.ManyToManyField(Table, blank=True)

    def __str__(self):
        selected_tables = ", ".join([str(table) for table in self.tables.all()])
        return f"Selected tables from {self.data_source}: {selected_tables}"
