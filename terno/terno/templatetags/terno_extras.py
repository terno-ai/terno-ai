from django import template

register = template.Library()


@register.filter(name='table_schema')
def table_schema(mdb, table_name):
    """Get schema for a specific table"""
    return mdb.generate_schema(table_name)
