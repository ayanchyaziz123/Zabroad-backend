from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Like, Comment


@receiver(post_save, sender=Like)
def notify_on_like(sender, instance, created, **kwargs):
    if not created:
        return
    post   = instance.post
    liker  = instance.user
    author = post.author
    if liker == author:
        return  # don't notify on self-like

    from notifications.models import Notification
    liker_name = liker.get_full_name() or liker.username
    Notification.objects.create(
        recipient=author,
        sender=liker,
        type='like',
        title=f'{liker_name} liked your post',
        body=post.body[:120] + ('…' if len(post.body) > 120 else ''),
        post_id=post.pk,
    )


@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    if not created:
        return
    post      = instance.post
    commenter = instance.author
    author    = post.author
    if commenter == author:
        return  # don't notify on self-comment

    from notifications.models import Notification
    commenter_name = commenter.get_full_name() or commenter.username
    preview = instance.body[:80] + ('…' if len(instance.body) > 80 else '')
    Notification.objects.create(
        recipient=author,
        sender=commenter,
        type='comment',
        title=f'{commenter_name} commented on your post',
        body=f'"{preview}"',
        post_id=post.pk,
    )
