from __future__ import absolute_import

from rest_framework import serializers
from rest_framework.response import Response

from sentry import features
from sentry.api.bases.organization import OrganizationEndpoint
from sentry.api.paginator import OffsetPaginator
from sentry.api.serializers import serialize
from sentry.models import Integration


class IntegrationSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=64, required=True)


class OrganizationIntegrationsEndpoint(OrganizationEndpoint):
    def has_feature(self, request, organization):
        return features.has(
            'organizations:integrations-v3',
            organization=organization,
            actor=request.user,
        )

    def get(self, request, organization):
        if not self.has_feature(request, organization):
            return Response({'detail': ['You do not have that feature enabled']}, status=400)

        return self.paginate(
            queryset=Integration.objects.filter(organizations=organization),
            request=request,
            order_by='name',
            on_results=lambda x: serialize(x, request.user),
            paginator_cls=OffsetPaginator,
        )
