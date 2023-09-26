from django import template
from django.http import HttpRequest
from django.urls import reverse


register = template.Library()


@register.simple_tag
def active_link(request: HttpRequest, view_name: str) -> str:
    current_url = request.path
    target_url = reverse(view_name)

    if current_url == target_url:
        return "active"
    else:
        return ""