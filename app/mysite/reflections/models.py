# Django imports
from django.db import models
from django.utils.functional import cached_property
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey

# Additional dependencies
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import StreamField

# Wagtail (& friends) imports
from wagtail.core.models import Page
from wagtail.search import index

# local imports
from mysite.base.blocks import CustomRichTextBlock


class DevotionalTag(TaggedItemBase):
    content_object = ParentalKey("DailyReflectionPage", related_name="tagged_items", on_delete=models.CASCADE)


class DailyReflectionPage(Page):
    """
    The Daily Reflection Model

    Each DailyReflection should at least have
        - a date
        - Scripture reference
        - Content

    Optionally, there could be
        - additional resources
    """

    # administrative field(s)
    tags = ClusterTaggableManager(through=DevotionalTag, blank=True)

    # core fields
    reflection_date = models.DateField("Reflection Date", max_length=254)
    scripture = models.CharField("Scripture", max_length=254)
    content = StreamField(CustomRichTextBlock(), verbose_name="Main Content", max_num=1)

    # optional fields
    additional_resources = StreamField(
        CustomRichTextBlock(required=False),
        verbose_name="Additional Resources",
        help_text="optional additional resources (references, etc.)",
        blank=True,
    )
    # there could be more optional fields ...

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("scripture", classname="full"),
                FieldRowPanel([FieldPanel("reflection_date"), FieldPanel("tags")]),
            ],
            heading="Metadata",
            classname="collapsible",
        ),
        # content
        StreamFieldPanel("content"),
        # optional
        MultiFieldPanel(
            [
                StreamFieldPanel("additional_resources"),
                # there could be other panels here
            ],
            heading="Optional Extras",
            classname="collapsible",
        ),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("title", partial_match=True),
        index.SearchField("content", partial_match=True),
        index.SearchField("scripture", partial_match=True),
    ]

    @cached_property
    def date(self):
        """
        Returns the Reflection's date as a string in %Y-%m-%d format
        """
        fmt = "%Y-%m-%d"
        date_as_string = (self.reflection_date).strftime(fmt)
        return date_as_string

    @cached_property
    def date_alt(self):
        """
        Returns the Reflection's date
        as a string in %Y-%b-%d-%a format
        """
        fmt = "%Y-%b-%d-%a"
        date_as_string = (self.reflection_date).strftime(fmt)
        return date_as_string

    @cached_property
    def optional_extras(self):

        extras = [
            ("additional_resources", self.additional_resources),
            # there could be more here
        ]

        lean_exras = []

        for exra in extras:
            if exra[1]:  # we are only interested in non-null exras
                lean_exras.append(exra)

        return lean_exras

    @property
    def get_tags(self):
        """
        We're returning all the tags that are related to the daily reflection into a
        list we can access on the template. We're additionally adding a URL to
        access DailyReflectionPage objects with that tag
        """
        tags = self.tags.all()
        for tag in tags:
            tag.url = "/" + "/".join(s.strip("/") for s in [self.get_parent().url, "tags", tag.slug])
        return tags

    @property
    def next_dailyreflection(self):
        # https://docs.djangoproject.com/en/3.2/ref/models/instances/#django.db.models.Model.get_next_by_FOO
        return self.get_next_by_reflection_date()

    @property
    def previous_dailyreflection(self):
        # https://docs.djangoproject.com/en/3.2/ref/models/instances/#django.db.models.Model.get_previous_by_FOO
        return self.get_previous_by_reflection_date()

    # Specifies parent to DailyReflectionPage as being HomePage
    parent_page_types = ["home.HomePage"]

    # Specifies what content types can exist as children of DailyReflectionPage.
    # Empty list means that no child content types are allowed.
    subpage_types = []

    def __str__(self):
        return "{}".format(self.date)

    def get_admin_display_title(self):
        return "{} » {}".format(self.date_alt, self.draft_title)

    def get_context(self, request):
        # context = super().get_context(request)
        context = super(DailyReflectionPage, self).get_context(request)
        return context

    def full_clean(self, *args, **kwargs):
        # first call the built-in cleanups (including default slug generation)
        super(DailyReflectionPage, self).full_clean(*args, **kwargs)

        # now make your additional modifications
        if self.slug is not self.date:
            self.slug = self.date

    class Meta:
        verbose_name = "Daily Reflection"
        verbose_name_plural = "Daily Reflections"
