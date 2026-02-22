import logging

logger = logging.getLogger(__name__)


def send_notification(requester_email, pr_number, new_status, comment=None):
    """Send email notification to requester on status change.

    Currently stubbed — logs the notification instead of sending email.
    Wire up SMTP when ready by implementing the actual send logic.
    """
    message = (
        f"[EMAIL STUB] To: {requester_email} | "
        f"PR #{pr_number} status changed to '{new_status}'"
    )
    if comment:
        message += f" | Comment: {comment}"

    logger.info(message)
