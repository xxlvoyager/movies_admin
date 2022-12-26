from rest_framework import viewsets
from rest_framework import pagination, permissions
from api.serializers import FilmSerializer
from rest_framework.response import Response

from movies.models import FilmWork


class CustomPagination(pagination.PageNumberPagination):
    page_size = 50

    def get_paginated_response(self, data):
        return Response({
            'page': self.page.number,
            'next': self.page.next_page_number() if self.page.has_next() else None,
            'previous': self.page.previous_page_number() if self.page.has_previous() else None,
            'total_pages': self.page.paginator.count,
            'results': data
        })


class FilmsViewSet(viewsets.ModelViewSet):
    """
    API endpoint
    """
    queryset = FilmWork.objects.all().order_by('id')
    serializer_class = FilmSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
