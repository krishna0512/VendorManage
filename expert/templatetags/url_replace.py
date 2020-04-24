from urllib.parse import urlencode
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    if not kwargs:
        return query.urlencode()
    for i in kwargs:
        query[i] = kwargs[i]
    return query.urlencode()