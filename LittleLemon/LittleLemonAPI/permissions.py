from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsManagerOrAdminOrReadOnly(BasePermission):
    """Allow read-only access to anyone, but write access only to superusers or users in the 'Manager' group.

    Rules:
    - SAFE_METHODS (GET, HEAD, OPTIONS): always allowed.
    - Other methods: user must be authenticated AND (is_superuser OR belongs to 'Manager').
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.groups.filter(name='Manager').exists()


class IsManagerOrAdmin(BasePermission):
    """Allow access only to superusers or users in the 'Manager' group for any method.

    Useful for admin/manager-only endpoints (including GET).
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.groups.filter(name='Manager').exists()


class IsCustomer(BasePermission):
    """Allow only authenticated users who are NOT managers, NOT delivery crew, and NOT superusers."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return False
        # Customers are users not in Manager nor Delivery Crew groups
        return not user.groups.filter(name__in=['Manager', 'Delivery Crew']).exists()
