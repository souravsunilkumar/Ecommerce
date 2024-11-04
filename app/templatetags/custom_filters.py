from django import template

register = template.Library()

@register.filter
def get_images_by_product(images_by_product, product_id):
    return images_by_product.get(product_id, [])

@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except (TypeError, ValueError):
        return value