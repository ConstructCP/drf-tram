from rest_framework.permissions import IsAdminUser, IsAuthenticated


class IsOwner(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
