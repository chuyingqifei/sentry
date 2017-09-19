from __future__ import absolute_import, print_function

__all__ = ['PipelineHelper']

import logging

from django.contrib import messages
from django.http import HttpResponseRedirect

from sentry.models import Integration
from sentry.utils.hashlib import md5_text
from sentry.utils.http import absolute_uri
from sentry.web.helpers import render_to_response

from . import default_manager

SESSION_KEY = 'integration.setup'

logger = logging.getLogger('sentry.integrations')


class PipelineHelper(object):
    @classmethod
    def get_for_request(cls, request, organization, provider_id):
        provider = default_manager.get(provider_id)
        session = request.session.get(SESSION_KEY, {})
        if not session:
            logger.error('integrations.setup.invalid-session-data')
            return cls(request, organization, provider)

        if session.get('int'):
            integration = Integration.objects.get(
                id=session['int'],
                organization_id=organization.id,
            )
        else:
            integration = None

        instance = cls(
            request,
            organization=organization,
            integration=integration,
            provider=provider,
            step=session['step'],
        )
        if instance.signature != session['sig']:
            logger.error('integrations.setup.invalid-signature')
            return cls(request, organization, provider)
        return instance

    def __init__(self, request, organization, provider, integration=None,
                 step=0, state=None):
        self.request = request
        self.integration = integration
        self.organization = organization
        self.provider = provider
        self.pipeline = provider.get_pipeline()
        self.signature = md5_text(*[
            '{module}.{name}'.format(
                module=type(v).__module__,
                name=type(v).__name__,
            ) for v in self.pipeline
        ]).hexdigest()
        self.step = step
        self.state = state or {}

    def save_session(self):
        self.request.session[SESSION_KEY] = {
            'uid': self.request.user.id,
            'org': self.organization.id,
            'pro': self.provider.id,
            'int': self.integration.id if self.integration else '',
            'sig': self.signature,
            'step': self.step,
            'state': {},
        }
        self.request.session.modified = True

    def get_redirect_url(self):
        return absolute_uri('/organizations/{}/integrations/{}/setup/'.format(
            self.organization.slug,
            self.provider.id,
        ))

    def clear_session(self):
        if SESSION_KEY in self.request.session:
            del self.request.session[SESSION_KEY]
            self.request.session.modified = True

    def current_step(self):
        """
        Render the current step.
        """
        if self.step == len(self.pipeline):
            return self.finish_pipeline()
        return self.pipeline[self.step].dispatch(
            request=self.request,
            helper=self,
        )

    def next_step(self):
        """
        Render the next step.
        """
        self.step += 1
        self.save_session()
        return self.current_step()

    def finish_pipeline(self):
        metadata = self.provider.build_metadata(self.state)
        response = self._finish_pipeline(metadata)
        return response

    def respond(self, template, context=None, status=200):
        default_context = {
            'organization': self.organization,
            'provider': self.provider,
        }
        if context:
            default_context.update(context)

        return render_to_response(template, default_context, self.request, status=status)

    def error(self, message):
        messages.add_message(
            self.request,
            messages.ERROR,
            u'There was an error setting up {}: {}'.format(self.provider.name, message),
        )

        redirect_uri = '/organizations/{}/integrations/'.format(
            self.organization.slug,
        )
        return HttpResponseRedirect(redirect_uri)

    def bind_state(self, key, value):
        self.state[key] = value
        self.save_session()

    def fetch_state(self, key):
        return self.state.get(key)

    def _finish_pipeline(self, metadata):
        if self.integration:
            self.integration.update(
                metadata=metadata,
            )
        else:
            self.integration = Integration.objects.create(
                provider=self.provider.id,
                metadata=metadata,
            )
            self.integration.add_organization(self.organization.id)
