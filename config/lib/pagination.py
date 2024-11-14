# create by: ayoub taneh (2024-08-07)
from rest_framework.pagination import PageNumberPagination as DefaultPageNumberPagination
from config.lib.ApiResponse import ApiResponse
from django.conf import settings


class PageNumberPagination(DefaultPageNumberPagination):
    """Custom Pagination
    -------------- add to setting.py --------------
        REST_FRAMEWORK = {
            'DEFAULT_PAGINATION_CLASS': 'config.lib.pagination.PageNumberPagination',
            'PAGE_SIZE': 200,
            'MAX_PAGE_SIZE': 500,
            'CURRENT_PAGE_NAME': 'current_page',
            'PAGE_SIZE_QUERY_PARAM': 'page_size',
            'TOTAL_PAGES_QUERY_PARAM': 'total_pages',
        }
    -------------- use in Class --------------
        from config.custom_lib import PageNumberPagination,
        class ClassName(viewsets.ModelViewSet):
        
            # If you don't want to set in the setting.py file
            pagination_class = PageNumberPagination
            
            # If you set it in the settings file and you don't want it to be used on this page
            pagination_class = []
            
    """
    page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
    page_size_query_param = settings.REST_FRAMEWORK['PAGE_SIZE_QUERY_PARAM']
    max_page_size = settings.REST_FRAMEWORK['MAX_PAGE_SIZE']

    def get_paginated_response(self, data):
        request = self.request
        page_size = self.get_page_size(request)
        
        response = super().get_paginated_response(data)
        
        response.data[settings.REST_FRAMEWORK['TOTAL_PAGES_QUERY_PARAM']] = self.page.paginator.num_pages
        response.data[self.page_size_query_param] = page_size
        response.data[settings.REST_FRAMEWORK['CURRENT_PAGE_NAME']] = self.page.number
        return response.data

        '''
            1403/02/01 taneh create
            1403/05/17 taneh update
        '''