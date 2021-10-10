from django.conf import settings
from django.contrib.auth import get_user_model
from wagtail.admin.mail import EmailNotificationMixin, Notifier
from wagtail.core.models import TaskState

from mysite.reflections.models import SplitGroupApprovalTask


class BaseSplitGroupApprovalTaskStateEmailNotifier(EmailNotificationMixin, Notifier):
    """A base notifier to send updates for SplitGroupApprovalTask events"""

    def __init__(self):
        # Allow TaskState to send notifications
        super().__init__((TaskState))

    def can_handle(self, instance, **kwargs):
        if super().can_handle(instance, **kwargs) and isinstance(instance.task.specific, SplitGroupApprovalTask):
            # Don't send notifications if a Task has been cancelled and then resumed - ie page was updated to a new revision
            return not TaskState.objects.filter(
                workflow_state=instance.workflow_state,
                task=instance.task,
                status=TaskState.STATUS_CANCELLED,
            ).exists()
        return False

    def get_context(self, task_state, **kwargs):
        context = super().get_context(task_state, **kwargs)
        context["page"] = task_state.workflow_state.page
        context["task"] = task_state.task.specific
        return context

    def get_recipient_users(self, task_state, **kwargs):

        triggering_user = kwargs.get("user", None)

        approval_groups = task_state.task.specific.get_approval_groups(task_state.workflow_state.page)

        group_members = get_user_model().objects.filter(groups__in=approval_groups.all())

        recipients = group_members

        include_superusers = getattr(settings, "WAGTAILADMIN_NOTIFICATION_INCLUDE_SUPERUSERS", True)
        if include_superusers:
            superusers = get_user_model().objects.filter(is_superuser=True)
            recipients = recipients | superusers

        if triggering_user:
            recipients = recipients.exclude(pk=triggering_user.pk)

        return recipients


class SplitGroupApprovalTaskStateSubmissionEmailNotifier(BaseSplitGroupApprovalTaskStateEmailNotifier):
    """A notifier to send updates for SplitGroupApprovalTask submission events"""

    notification = "submitted"
