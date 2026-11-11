from rest_framework.permissions import SAFE_METHODS, BasePermission
 
 
class AuthenticatedWriteAdminDelete(BasePermission):
 
    message = 'Недостатньо прав: видаляти записи можуть лише адміністратори.'
 
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not (user and user.is_authenticated):
            return False  # DRF перетворить це на 401, бо JWT має authenticate_header
        if request.method == 'DELETE':
            return user.is_staff
        return True