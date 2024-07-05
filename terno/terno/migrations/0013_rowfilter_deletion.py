# Created by Sandeep Giri manually

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terno', '0012_rename_tablerowfilterselector_tablerowfilter'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GroupTableRowFilter',
        ),
        migrations.DeleteModel(
            name='TableRowFilter',
        ),
    ]
