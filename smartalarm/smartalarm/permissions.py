from rest_framework import permissions
from django.core.exceptions import ImproperlyConfigured


class HasAccessToResource(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        resource = self.get_resource(view)

        # Validate if user have access to resource
        if resource.user == user:
            return True

        return False

    def get_resource(self, view):
        try:
            return getattr(view, 'get_resource')()
        except AttributeError:
            raise ImproperlyConfigured(
                'HasAccessToResource requires the view to have the get_resource() method')