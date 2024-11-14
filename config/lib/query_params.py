# create by: ayoub taneh (2024-08-07)
from django.conf import settings
from config.lib.utils import cbool

    
class QueryParams:
    # create by: ayoub taneh (2024-08-07)
    
    def get_page_size(self, request):
        """Get page_size from the client, If it was not sent, it will use the default from setting.py
            add to setting.py
                settings.REST_FRAMEWORK['PAGE_SIZE']
                settings.REST_FRAMEWORK['PAGE_SIZE_QUERY_PARAM']
        """
        page_number = request.query_params.get(settings.REST_FRAMEWORK['PAGE_SIZE_QUERY_PARAM'])
        
        if page_number and page_number.isdigit():
            return int(page_number)
        else:
            return settings.REST_FRAMEWORK['PAGE_SIZE']
        
        ''' FOR USE FROM CODES
        
            from config.custom_lib import Queryset
            
            class ClassName(viewsets.ModelViewSet):
                .
                .
            
            def get_queryset(self):
                _queryset = Queryset()
                self.pagination_class.page_size = _queryset.get_page_size(self.request)
                return super().get_queryset()
                1403/02/01 taneh
        '''
        
        
    def check_perfect(self, request):
        """If sent perfect=true, returns all fields with joins to tables"""
        return cbool(request.query_params.get('perfect', False))
            
            

    def get_search_fields(self, request, default_search_fields=[]):            
        """If there is a field or fields entered for search, it uses them, 
            otherwise it uses the default value that is in the codes.
            
            send: url.com?search_fields=field1,field2,...
        """
        search_fields = request.query_params.get('search_fields')
        if search_fields:
            
            if ',' in search_fields:
                return search_fields.split(',')
            else:  
                return [search_fields]
            
        else:
            return default_search_fields
        
        ''' FOR USE FROM CODES
        
            from rest_framework.pagination import PageNumberPagination
            
            class ClassName(viewsets.ModelViewSet):
                .
                .
                pagination_class = PageNumberPagination
                filter_backends = [SearchFilter]
            
            def list(self, request, *args, **kwargs):
                SearchFields = SearchFields()
                self.search_fields = SearchFields.get_search_fields(request, ['parent'])
                return super().list(request, *args, **kwargs)
                1403/02/01 taneh
        '''

