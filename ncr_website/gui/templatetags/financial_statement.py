"""This module defines template tags used to render financial statements."""
from django import template


register = template.Library()


@register.simple_tag
def item_value(period, item_name):
    """Return the value of a financial statement item."""

    # Make sure there is a period object to parse
    if period is not None:

        split_item_name = item_name.split('.')

        # Example: balance_sheet.non_current_assets.property_plant_equipment
        z = period
        for x in split_item_name:

            z = getattr(z, x)

        try:
            v = getattr(z, 'value')
        except AttributeError:
            v = z

        return v


@register.filter
def escape_slash(parameter):
    """Convert / to :: for urls. Can be removed with path: in url
    after updating to Django 2.0."""

    return parameter.replace('/', '::')


@register.filter
def reverse_escape_slash(parameter):
    """Convert :: to / from urls. Can be removed with path: in url
    after updating to Django 2.0."""

    return parameter.replace('::', '/')
