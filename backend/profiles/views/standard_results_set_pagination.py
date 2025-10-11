"""
Django REST Framework pagination class that controls how list endpoints return results.
"""

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Django REST Framework pagination class that controls how list endpoints return results.
    """
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 200
