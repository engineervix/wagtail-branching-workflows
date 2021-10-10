from wagtail.core.signals import task_submitted

from mysite.reflections.mail import SplitGroupApprovalTaskStateSubmissionEmailNotifier

task_submission_email_notifier = SplitGroupApprovalTaskStateSubmissionEmailNotifier()


def register_signal_handlers():
    task_submitted.connect(
        task_submission_email_notifier,
        dispatch_uid="task_submitted_email_notification",
    )
