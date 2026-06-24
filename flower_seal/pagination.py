from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from django.core.paginator import InvalidPage

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view)
        except (NotFound, InvalidPage):
            # Fall back to page 1 if the requested page is out of bounds
            paginator = self.django_paginator_class(queryset, self.get_page_size(request))
            try:
                self.page = paginator.page(1)
                return list(self.page)
            except InvalidPage:
                return []
