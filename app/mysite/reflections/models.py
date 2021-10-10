# Django imports
from django import forms
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
from wagtail.core.models import Group, Page, Task, TaskState, WorkflowState
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
    def date_in_first_semester(self):
        """
        Returns True if Reflection's date
        is in the first half of the year
        """
        month = (self.reflection_date).month
        return month <= 6

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

    def get_approval_group_key(self):
        # custom logic here that checks all the date stuff
        if self.date_in_first_semester:
            return "A"
        return "B"

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


class SplitGroupApprovalTask(Task):

    ## note: this is the simplest approach, two fields of linked groups, you could further refine this approach as needed.

    groups_a = models.ManyToManyField(
        Group,
        verbose_name="for Jan - June Daily Reflections",
        help_text="Pages at this step in a workflow will be moderated or approved by these groups of users",
        related_name="split_task_group_a",
    )
    groups_b = models.ManyToManyField(
        Group,
        verbose_name="for Jul - Dec Daily Reflections",
        help_text="Pages at this step in a workflow will be moderated or approved by these groups of users",
        related_name="split_task_group_b",
    )

    admin_form_fields = Task.admin_form_fields + ["groups_a", "groups_b"]
    admin_form_widgets = {
        "groups_a": forms.CheckboxSelectMultiple,
        "groups_b": forms.CheckboxSelectMultiple,
    }

    def get_approval_groups(self, page):
        """This method gets used by all checks when determining what group to allow/assign this Task to"""

        # recommend some checks here, what if `get_approval_group` is not on the Page?

        # here's a simple check
        if hasattr(page.specific, "get_approval_group_key"):
            approval_group = page.specific.get_approval_group_key()
        else:
            # arbitrarily assign to group A
            # (you could instead do something else)
            approval_group = "A"

        if approval_group == "A":
            return self.groups_a

        return self.groups_b

    # each of the following methods will need to be implemented, all checking for the correct groups for the Page when called
    # def start(self, ...etc)
    # def user_can_access_editor(self, ...etc)
    # def page_locked_for_user(self, ...etc)
    # def user_can_lock(self, ...etc)
    # def user_can_unlock(self, ...etc)
    # def get_task_states_user_can_moderate(self, ...etc)

    def start(self, workflow_state, user=None):
        # essentially a copy of this method on `GroupApprovalTask` but with the ability to have a dynamic 'group' returned.
        approval_groups = self.get_approval_groups(workflow_state.page)

        if workflow_state.page.locked_by:
            # If the person who locked the page isn't in one of the groups, unlock the page
            # if not workflow_state.page.locked_by.groups.filter(id__in=self.groups.all()).exists():
            if not approval_groups.filter(id__in=self.groups.all()).exists():
                workflow_state.page.locked = False
                workflow_state.page.locked_by = None
                workflow_state.page.locked_at = None
                workflow_state.page.save(update_fields=["locked", "locked_by", "locked_at"])

        return super().start(workflow_state, user=user)

    def user_can_access_editor(self, page, user):
        # essentially a copy of this method on `GroupApprovalTask` but with the ability to have a dynamic 'group' returned.
        approval_groups = self.get_approval_groups(page)

        # return self.groups.filter(id__in=user.groups.all()).exists() or user.is_superuser
        return approval_groups.filter(id__in=user.groups.all()).exists() or user.is_superuser

    def page_locked_for_user(self, page, user):
        # essentially a copy of this method on `GroupApprovalTask` but with the ability to have a dynamic 'group' returned.
        approval_groups = self.get_approval_groups(page)

        # return not (self.groups.filter(id__in=user.groups.all()).exists() or user.is_superuser)
        return not (approval_groups.filter(id__in=user.groups.all()).exists() or user.is_superuser)

    def user_can_lock(self, page, user):
        # essentially a copy of this method on `GroupApprovalTask` but with the ability to have a dynamic 'group' returned.
        approval_groups = self.get_approval_groups(page)

        # return self.groups.filter(id__in=user.groups.all()).exists()
        return approval_groups.filter(id__in=user.groups.all()).exists()

    def user_can_unlock(self, page, user):
        # essentially a copy of this method on `GroupApprovalTask` but with the ability to have a dynamic 'group' returned.
        # approval_groups = self.get_approval_groups(page)
        return False

    def get_actions(self, page, user):
        # essentially a copy of this method on `GroupApprovalTask` but with the ability to have a dynamic 'group' returned.
        approval_groups = self.get_approval_groups(page)

        if approval_groups.filter(id__in=user.groups.all()).exists() or user.is_superuser:
            return [
                ("reject", "Request changes", True),
                ("approve", "Approve", False),
                ("approve", "Approve with comment", True),
            ]

        return super().get_actions(page, user)

    def get_task_states_user_can_moderate(self, user, **kwargs):

        # not a very DRY approach, but it works!

        if user.is_superuser:
            return TaskState.objects.filter(status=TaskState.STATUS_IN_PROGRESS, task=self.task_ptr)
        elif self.groups_a.filter(id__in=user.groups.all()).exists():
            return TaskState.objects.filter(
                status=TaskState.STATUS_IN_PROGRESS,
                task=self.task_ptr,
                workflow_state__in=WorkflowState.objects.filter(
                    page__in=DailyReflectionPage.objects.filter(reflection_date__month__lte=6)
                ),
            )
        elif self.groups_b.filter(id__in=user.groups.all()).exists():
            return TaskState.objects.filter(
                status=TaskState.STATUS_IN_PROGRESS,
                task=self.task_ptr,
                workflow_state__in=WorkflowState.objects.filter(
                    page__in=DailyReflectionPage.objects.filter(reflection_date__month__gt=6)
                ),
            )
        else:
            return TaskState.objects.none()

    @classmethod
    def get_description(cls):
        return "Groups are assigned to approve this task based on reflection month"

    class Meta:
        verbose_name = "reflection-month-dependent approval task"
        verbose_name_plural = "reflection-month-dependent approval tasks"
