from rest_framework.permissions import BasePermission, SAFE_METHODS


class CanAccessDraftReport(BasePermission):
    """
    Admin hanya dapat melihat laporan non-DRAFT dan hanya boleh mengubah status.
    Citizen dapat melihat laporan non-DRAFT serta semua laporan miliknya sendiri.
    Citizen hanya boleh membuat, mengubah, dan menghapus laporan miliknya sendiri.
    """

    message = 'Anda tidak memiliki izin untuk mengakses laporan ini.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if view.action == 'create':
            return not getattr(user, 'is_admin', False)

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_admin = getattr(user, 'is_admin', False)
        is_owner = obj.reporter_id == user.id

        if request.method in SAFE_METHODS:
            if is_admin:
                return obj.status != 'DRAFT'
            return obj.status != 'DRAFT' or is_owner

        if obj.status == 'RESOLVED':
            return False

        if is_admin:
            return view.action in ['update', 'partial_update']

        return (
            is_owner
            and obj.status == 'DRAFT'
            and view.action in ['update', 'partial_update', 'destroy']
        )
