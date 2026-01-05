from django import template
from ..models import Group

register = template.Library()

@register.inclusion_tag('goods/menu.html')
def render_menu():
    root_groups = Group.objects.filter(parent__isnull=True, is_included_in_menu=True, is_group_modifier=False).order_by('order')
    return {'groups': root_groups}

