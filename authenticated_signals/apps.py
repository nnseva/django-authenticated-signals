from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

import uuid

from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from .signals import authenticated_pre_save, authenticated_post_save, authenticated_pre_delete, authenticated_post_delete

from .middleware import current_request


def pre_save_translate(sender, *av, **kw):
    authenticated_pre_save.send(
        sender,
        request=current_request(),
        *av,
        **{k: kw[k] for k in kw if k != 'signal'}
    )


def post_save_translate(sender, *av, **kw):
    authenticated_post_save.send(
        sender,
        request=current_request(),
        *av,
        **{k: kw[k] for k in kw if k != 'signal'}
    )


def pre_delete_translate(sender, *av, **kw):
    authenticated_pre_delete.send(
        sender,
        request=current_request(),
        *av,
        **{k: kw[k] for k in kw if k != 'signal'}
    )


def post_delete_translate(sender, *av, **kw):
    authenticated_post_delete.send(
        sender,
        request=current_request(),
        *av,
        **{k: kw[k] for k in kw if k != 'signal'}
    )


class AuthenticatedSignalsConfig(AppConfig):
    name = 'authenticated_signals'
    verbose_name = _("Authenticated Signals")

    def ready(self):
        dispatch_uid = uuid.uuid4()

        pre_save.connect(pre_save_translate, dispatch_uid=dispatch_uid)
        post_save.connect(post_save_translate, dispatch_uid=dispatch_uid)

        pre_delete.connect(pre_delete_translate, dispatch_uid=dispatch_uid)
        post_delete.connect(post_delete_translate, dispatch_uid=dispatch_uid)
