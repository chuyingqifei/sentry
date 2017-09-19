from __future__ import absolute_import

import six

from sentry.api.serializers import register, Serializer
from sentry.models import Integration


@register(Integration)
class IntegrationSerializer(Serializer):
    def serialize(self, obj, attrs, user):
        return {
            'id': six.text_type(obj.id),
            'name': obj.name,
            'provider': {
                'id': obj.provider,
            }
        }