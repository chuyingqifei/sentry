from __future__ import absolute_import

from django.http import HttpResponse
from sentry.integrations import Integration, PipelineView


class ExampleSetupView(PipelineView):
    TEMPLATE = '<form method="POST"><input type="email" name="email" /></form>'

    def dispatch(self, request, helper):
        if 'name' in request.POST:
            helper.bind_state('name', request.POST['name'])
            return helper.next_step()

        return HttpResponse(self.TEMPLATE)


class ExampleIntegration(Integration):
    """
    An example integration, generally used for testing.
    """
    id = 'example'

    name = 'Example'

    def get_pipeline(self):
        return [
            ExampleSetupView(PipelineView),
        ]

    def get_config(self):
        return [{
            'name': 'name',
            'label': 'Name',
            'type': 'text',
            'required': True,
        }]

    def setup(self):
        """
        Executed once Sentry has been initialized at runtime.

        >>> def setup(self):
        >>>     bindings.add('repository.provider', GitHubRepositoryProvider, id='github')
        """
