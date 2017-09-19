from __future__ import absolute_import, print_function

__all__ = ['PipelineView']

from sentry.web.frontend.base import BaseView


class PipelineView(BaseView):
    auth_required = True
    sudo_required = False
