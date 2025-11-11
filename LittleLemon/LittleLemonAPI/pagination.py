from rest_framework.pagination import PageNumberPagination

class MenuItemsPagination(PageNumberPagination):
    # Default items per page if the client doesn't specify
    page_size = 10
    # Client can override page size using ?number_pages=XX
    page_size_query_param = 'number_pages'
    # Put a reasonable upper bound to avoid huge responses
    max_page_size = 100
