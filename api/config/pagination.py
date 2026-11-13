"""Default pagination for the API."""
from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Five results per page, with an optional client-side page size cap."""

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 50
