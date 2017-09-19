from __future__ import absolute_import, print_function

from sentry import features
from sentry.integrations.helper import PipelineHelper
from sentry.web.frontend.base import OrganizationView


class IntegrationSetupView(OrganizationView):
    required_scope = 'org:integrations'

    def has_feature(self, request, organization):
        return features.has(
            'organizations:integrations-v3',
            organization=organization,
            actor=request.user,
        )

    def handle(self, request, organization, provider_id):
        if not self.has_feature(request, organization):
            return self.redirect('/')

        helper = PipelineHelper.get_for_request(
            request,
            organization,
            provider_id,
        )
        return helper.current_step()
