from rest_framework import permissions


class ReadAnyoneWriteAdmin(permissions.IsAdminUser):

    def has_permission(self, request, view):
        is_admin = super(ReadAnyoneWriteAdmin, self).has_permission(request, view)
        return request.method in permissions.SAFE_METHODS or is_admin
