from django.db import migrations


def assign_or_create_llm_credit(apps, schema_editor):
    Organisation = apps.get_model('terno', 'Organisation')
    LLMCredit = apps.get_model('subscription', 'LLMCredit')

    for organisation in Organisation.objects.all():
        if organisation.subdomain == 'terno-root':
            continue
        owner = organisation.owner
        try:
            llm_credit = LLMCredit.objects.get(owner=owner)
        except LLMCredit.DoesNotExist:
            llm_credit = LLMCredit.objects.create(owner=owner, credit=10.0)

        organisation.llm_credit = llm_credit
        organisation.save()


class Migration(migrations.Migration):

    dependencies = [
        ('terno', '0040_organisation_llm_credit'),
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(assign_or_create_llm_credit),
    ]
