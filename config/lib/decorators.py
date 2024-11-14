from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext as _



def queryset_order_by_field(field_name='created_at', sort='-'):
    """Decorator to `order_by` the queryset by a specific field.

    This decorator modifies the queryset of the view by ordering it based on 
    the provided field name and sort direction. By default, it orders by 
    the 'created_at' field in descending order.

    Args:
        field_name (str, optional): The name of the field to order the queryset by. 
                                    Defaults to 'created_at'.
        sort (str, optional): The sort direction. Use '-' for descending order or 
                              an empty string for ascending order. Defaults to '-'.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            self.queryset = self.queryset.order_by(f"{sort}{field_name}")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def queryset_filter_by_deleted(param_name='deleted', field_name='deleted_at'):
    """Decorator to filter the queryset based on the specified query parameter.

    This decorator modifies the queryset of the view by filtering it 
    according to whether the specified parameter is set to 'true' or 'false'.
    By default, it filters for non-deleted records if the parameter is not provided.

    Args:
        param_name (str, optional): The name of the query parameter to check for deletion status. Defaults to 'deleted'.
        field_name (str, optional): The field name to filter on for deletion status. Defaults to 'deleted_at'.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            deleted = self.request.query_params.get(param_name, 'false')
            if deleted == 'true':
                self.queryset = self.queryset.filter(**{f"{field_name}__isnull": False})
            else:
                self.queryset = self.queryset.filter(**{f"{field_name}__isnull": True})
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def queryset_by_field_for_user(param_name='bizid', field_name='business', get_from='headers'):
    """Decorator to filter the queryset based on the 'bizid' header/query parameter 
    and user permissions.

    This decorator filters the queryset if the 'bizid' value is provided and the user 
    is either a superuser or a regular user. If the user is a superuser and 'bizid' is present,
    the queryset is filtered by the provided 'bizid'. For non-superusers, it always applies 
    the filter.

    Args:
        param_name (str, optional): The name of the parameter to check for business ID. Defaults to 'bizid'.
        field_name (str, optional): The field name to filter on for the business. Defaults to 'business'.
        get_from (str, optional): The source to get the param ('headers' or 'query_params'). Defaults to 'headers'.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            param_source = getattr(self.request, get_from, None)
            if param_source:
                id = param_source.get(param_name)
                if (self.request.user.is_superuser and id is not None) or (not self.request.user.is_superuser):
                    self.queryset = self.queryset.filter(**{field_name: id})
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def queryset_by_field_if_not_null(param_name, field_name=None, get_from='query_params'):
    """Decorator to filter the queryset based on the specified parameter and field.

    This decorator filters the queryset if the specified parameter value is provided and not null.
    If the parameter value is present and not null, the queryset is filtered by the provided field name.
    
    If `field_name` is not provided, it defaults to the value of `param_name`.

    Args:
        param_name (str): The name of the parameter to check for in the request (e.g., 'partition').
        field_name (str, optional): The field name to filter on for the model (e.g., 'partition__id'). 
                                    If None, it defaults to the value of `param_name`.
        get_from (str, optional): The source to get the parameter from ('headers' or 'query_params'). 
                                  Defaults to 'query_params'.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            current_field_name = field_name if field_name is not None else param_name
            param_source = getattr(self.request, get_from, None)
            value = param_source.get(param_name) if param_source else None
            if value and value != 'null':
                self.queryset = self.queryset.filter(**{current_field_name: value})
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def queryset_by_field_or_null(param_name, field_name=None, get_from='query_params'):
    """Decorator to filter the queryset based on the specified parameter and field.

    This decorator filters the queryset if the specified parameter value is provided and not null.
    If the parameter value is present and not null, the queryset is filtered by the provided field name.
    
    If `field_name` is not provided, it defaults to the value of `param_name`.

    Args:
        param_name (str): The name of the parameter to check for in the request (e.g., 'partition').
        field_name (str, optional): The field name to filter on for the model (e.g., 'partition__id'). 
                                    If None, it defaults to the value of `param_name`.
        get_from (str, optional): The source to get the parameter from ('headers' or 'query_params'). 
                                  Defaults to 'query_params'.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            current_field_name = field_name if field_name is not None else param_name
            param_source = getattr(self.request, get_from, None)
            value = param_source.get(param_name) if param_source else None
            if value and value != 'null':
                self.queryset = self.queryset.filter(**{current_field_name: value})
                # print(f" in `if` param_name: {param_name} = {value}")
            else:
                self.queryset = self.queryset.filter(**{f"{current_field_name}__isnull": True})
                # print(f" in `else` param_name: {param_name} = {value}")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def queryset_by_field_or_null_bool(param_name, field_name=None, get_from='query_params', null_or_bool='null', superuser_only=False):
    """Decorator to filter the queryset based on the specified parameter and field.

    This decorator filters the queryset based on whether to check for boolean or null values.

    Args:
        param_name (str): The name of the parameter to check for in the request.
        field_name (str, optional): The field name to filter on for the model. If not provided, it defaults to the value of `param_name`.
        get_from (str, optional): The source to get the parameter from ('headers' or 'query_params').
        null_or_bool (str, optional): Specify 'bool' for boolean checks or 'null' for null checks. Defaults to 'null'.
        superuser_only (bool, optional): If True, only superusers can use this parameter for filtering. Defaults to False.

    If `null_or_bool` is 'bool', it filters as follows:
        - If `value` is None or 'true': filters to records where the field equals True.
        - If `value` is 'all': includes all records.
        - Otherwise, filters to records where the field equals False.

    If `null_or_bool` is 'null', it filters as follows:
        - If `value` is None, 'null', or 'false', filters to records where the field is null.
        - If `value` is 'all', includes all records.
        - Otherwise, filters to records where the field is not null.

    Superuser restrictions:
        - If `superuser_only` is set to True, only superusers can apply this filter. If a non-superuser tries to use this filter, the value is set to 'default' to bypass the filter and prevent unauthorized filtering.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            current_field_name = field_name if field_name is not None else param_name
            param_source = getattr(self.request, get_from, None)
            value = param_source.get(param_name) if param_source else None
            
            if superuser_only and not self.request.user.is_superuser:
                value = None # To cheat the situation
                    
            
            if null_or_bool == 'bool':
                if value is None or value == 'true':
                    self.queryset = self.queryset.filter(**{current_field_name: True})
                elif value != 'all':
                    self.queryset = self.queryset.filter(**{current_field_name: False})
                    
            else:
                if value is None or value == 'null' or value == 'false':
                    self.queryset = self.queryset.filter(**{f"{current_field_name}__isnull": True})
                elif value != 'all':
                    self.queryset = self.queryset.filter(**{f"{current_field_name}__isnull": False})

            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def queryset_by_field_value_or_null_or_ignore(param_name, field_name=None, get_from='query_params'):
    """Decorator to filter the queryset based on a specific parameter and field name.

    This decorator applies a filter to the queryset if a value for the specified parameter is provided in the request.
    If the parameter value is present:
        - If it equals 'null', the queryset is filtered to include only records where the specified field is null.
        - Otherwise, it filters by the provided field name using the parameter value.

    If `field_name` is not provided, it defaults to the value of `param_name`.

    Args:
        param_name (str): The name of the parameter to check in the request (e.g., 'partition').
        field_name (str, optional): The model field to filter on (e.g., 'partition__id').
                                    If not provided, it defaults to the value of `param_name`.
        get_from (str, optional): The request attribute to retrieve the parameter from ('headers' or 'query_params').
                                  Defaults to 'query_params'.

    Example:
        @queryset_by_field_value_or_null_or_ignore(param_name='partition', field_name='partition__id')
        def get_queryset(self):
            return MyModel.objects.all()
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            current_field_name = field_name if field_name is not None else param_name
            param_source = getattr(self.request, get_from, None)
            value = param_source.get(param_name) if param_source else None

            if value:
                if value == 'null':
                    self.queryset = self.queryset.filter(**{f"{current_field_name}__isnull": True})
                else:
                    self.queryset = self.queryset.filter(**{current_field_name: value})
            return func(self, *args, **kwargs)
        return wrapper
    return decorator



def check_dependencies(field_names, deleted_field='deleted_at'):
    """
    Decorator to check for dependencies before deleting an instance.
    
    - If any of the specified related fields (`field_names`) contain associated objects (have .exists()), 
      and the instance's `deleted_at` field is None (i.e., not soft-deleted), this decorator will raise a 
      ValidationError, preventing deletion.
    - This can be useful for ensuring that important relationships or dependencies are checked before allowing 
      deletion actions.
    
    Args:
    - field_names (list): A list of related field names (ForeignKey or ManyToMany fields) to check for dependencies.
    - deleted_at_field (str): The name of the field that indicates whether the instance is soft-deleted.
                              Default is 'deleted_at'.
    
    Example:
    ```
        @check_dependencies(['related_field_1', 'related_field_2'], deleted_at_field='deleted_at')
        def destroy(self, request, *args, **kwargs):
            # If any of the related fields have dependent records and deleted_at is None,
            # a ValidationError will be raised, preventing this method from proceeding.
            instance = self.get_object()
            instance.deleted_at = datetime.now()
            instance.save()
            return ApiResponse.success(self, _('Deleted successfully'), token=request.user.token)
    ```
    """
    def decorator(view_func):
        def wrapper(self, request, *args, **kwargs):
            instance = self.get_object()
            can_delete = True
            dependent_fields = [] 

            for field_name in field_names:
                related_instance = getattr(instance, field_name)

                if hasattr(related_instance, 'all'):
                    for related_obj in related_instance.all():
                        if getattr(related_obj, deleted_field) is None:
                            dependent_fields.append(field_name)
                            can_delete = False
                            break

                else:
                    if getattr(related_instance, deleted_field) is None:
                        dependent_fields.append(field_name)
                        can_delete = False

            if not can_delete:
                raise ValidationError(
                    _(f"Cannot delete this record because it is used by {', '.join(dependent_fields)}.")
                )

            return view_func(self, request, *args, **kwargs)

        return wrapper
    return decorator