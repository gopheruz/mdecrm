from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def unique_attr(items, attr):
    """Возвращает список уникальных значений атрибута"""
    seen = set()
    return [x[attr] for x in items if x[attr] not in seen and not seen.add(x[attr])]

@register.filter
def sum_attr(items, attr):
    """Суммирует значения атрибута"""
    return sum(item[attr] for item in items)

@register.filter
def map_attribute(list, attr):
    return [getattr(item, attr, None) for item in list]