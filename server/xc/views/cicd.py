from rest_framework.viewsets import ModelViewSet

from xc.models import Project, Version
from xc.serializers import ProjectSerializer, VersionSerializer
from xc.filters import ProjectFilter, VersionFilter

__all__ = ['ProjectViewSet', 'VersionViewSet']


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.order_by('-created_at')
    serializer_class = ProjectSerializer
    filterset_class = ProjectFilter
    search_fields = ['name']


class VersionViewSet(ModelViewSet):
    queryset = Version.objects.order_by('-start_time')
    serializer_class = VersionSerializer
    filterset_class = VersionFilter
    search_fields = ['name']

