from rest_framework.permissions import BasePermission, SAFE_METHODS


class CanAccessDraftReport(BasePermission):
    """
    Admin dapat mengakses semua laporan.
    Citizen hanya dapat mengakses laporan berstatus DRAFT miliknya sendiri.
    Laporan non-DRAFT dapat dibaca oleh user yang sudah login.
    Perubahan data oleh citizen hanya boleh dilakukan saat status masih DRAFT.
    """

    message = 'Anda tidak memiliki izin untuk mengakses laporan ini.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        if getattr(user, 'is_admin', False):
            return True

        is_owner = obj.reporter_id == user.id

        if request.method in SAFE_METHODS:
            if obj.status == 'DRAFT':
                return is_owner
            return True

        return is_owner and obj.status == 'DRAFT'
