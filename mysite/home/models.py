from django.db import models
from wagtail.core.models import Page


class HomePage(Page):
    search_fields = Page.search_fields
