from django.db import models
from wagtail.core.models import Page


class HomePage(Page):
    """
    Home Page
    """

    max_count = 1

    search_fields = Page.search_fields
