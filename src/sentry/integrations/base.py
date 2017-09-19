from __future__ import absolute_import

__all__ = ['Integration']

import logging


class Integration(object):
    """
    An integration describes a third party that can be registered within Sentry.

    The core behavior is simply how to add the integration (the authentication
    pipeline), and what kind of configuration is stored.

    This is similar to Sentry's legacy 'plugin' information, except that an
    integration is lives as an instance in the database, and the ``Integration``
    class is just a descriptor for how that object functions, and what behavior
    it provides (such as extensions provided).
    """

    # a unique identifier (e.g. 'slack')
    id = None

    # a human readable name (e.g. 'Slack')
    name = None

    def get_logger(self):
        return logging.getLogger('sentry.integration.%s' % (self.get_id(), ))

    def get_pipeline(self):
        """
        Return a list of ``View`` instances describing this integration's
        configuration pipeline.

        >>> def get_pipeline(self):
        >>>    return []
        """
        raise NotImplementedError

    # XXX(dcramer): this is not yet exposed anywhere in the UI
    def get_config(self):
        """
        Return a list of configuration attributes for this integration.

        The results of this are stored per-organization per-integration.

        >>> def get_config(self):
        >>>     return [{
        >>>         'name': 'instance',
        >>>         'label': 'Instance',
        >>>         'type': 'text',
        >>>         'placeholder': 'e.g. https://example.atlassian.net',
        >>>         'required': True,
        >>>     }]
        """
        raise NotImplementedError

    def build_metadata(self, state):
        """
        Given state captured during the setup pipeline, return a dictionary
        of metadata to store with this integration.

        This data **must not** be specified to an organization, as the
        integration may be shared among multiple organizations.

        This is the ideal place to store metadata like the 'name' or 'url' to
        the relevant entity, or shared API keys.

        >>> def get_metadata(self, state):
        >>>     return {
        >>>         'url': state['url'],
        >>>     }
        """
        return {}

    def setup(self):
        """
        Executed once Sentry has been initialized at runtime.

        >>> def setup(self):
        >>>     bindings.add('repository.provider', GitHubRepositoryProvider, id='github')
        """
