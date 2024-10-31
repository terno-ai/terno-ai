from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='table_schema')
@stringfilter
def table_schema(schema, table_name):
    """Get schema for a specific table"""
    return "table schema ------"
    try:
        tables = eval(schema)  # Be careful with eval, ensure schema is safe
        if table_name in tables:
            return str(tables[table_name])
        return ""
    except:
        return ""
