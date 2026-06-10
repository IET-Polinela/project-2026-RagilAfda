from rest_framework import serializers

from .models import Report


PUBLIC_STATUS_VALUES = {'REPORTED', 'VERIFIED', 'IN_PROGRESS', 'RESOLVED'}
CITIZEN_CREATE_STATUS_VALUES = {'DRAFT', 'REPORTED'}


class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    can_update_status = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id',
            'title',
            'category',
            'description',
            'location',
            'reporter',
            'is_owner',
            'can_edit',
            'can_delete',
            'can_update_status',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['reporter', 'created_at', 'updated_at']

    def get_reporter(self, obj):
        request = self.context.get('request')

        if not obj.reporter:
            return 'Warga Anonim'

        if not request or not request.user.is_authenticated:
            return 'Warga Anonim'

        user = request.user
        if getattr(user, 'is_admin', False) or obj.reporter_id == user.id:
            return obj.reporter.username

        return 'Warga Anonim'

    def get_is_owner(self, obj):
        request = self.context.get('request')

        if request and request.user and request.user.is_authenticated:
            return obj.reporter_id == request.user.id

        return False

    def get_can_update_status(self, obj):
        request = self.context.get('request')
        return bool(
            request
            and request.user
            and request.user.is_authenticated
            and getattr(request.user, 'is_admin', False)
            and obj.status != 'DRAFT'
        )

    def get_can_edit(self, obj):
        request = self.context.get('request')
        return bool(
            request
            and request.user
            and request.user.is_authenticated
            and not getattr(request.user, 'is_admin', False)
            and obj.reporter_id == request.user.id
        )

    def get_can_delete(self, obj):
        return self.get_can_edit(obj)

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return attrs

        user = request.user
        submitted_fields = set(self.initial_data.keys())

        if request.method == 'POST':
            submitted_status = attrs.get('status', 'REPORTED')
            if submitted_status not in CITIZEN_CREATE_STATUS_VALUES:
                raise serializers.ValidationError({
                    'status': 'Citizen hanya dapat membuat laporan sebagai DRAFT atau REPORTED.'
                })
            return attrs

        if getattr(user, 'is_admin', False):
            if request.method not in ['PUT', 'PATCH']:
                return attrs
            if submitted_fields != {'status'}:
                raise serializers.ValidationError(
                    'Admin hanya dapat memperbarui status laporan.'
                )
            if attrs.get('status') not in PUBLIC_STATUS_VALUES:
                raise serializers.ValidationError({
                    'status': 'Admin hanya dapat memilih status laporan non-draft.'
                })
            return attrs

        if request.method in ['PUT', 'PATCH']:
            if 'reporter' in submitted_fields:
                raise serializers.ValidationError({
                    'reporter': 'Citizen tidak dapat mengubah reporter laporan.'
                })

            if 'status' in submitted_fields:
                is_submitting_draft = (
                    self.instance
                    and self.instance.status == 'DRAFT'
                    and attrs.get('status') == 'REPORTED'
                )
                if not is_submitting_draft:
                    raise serializers.ValidationError({
                        'status': (
                            'Citizen hanya dapat mengajukan laporan miliknya '
                            'dari DRAFT menjadi REPORTED.'
                        )
                    })

        return attrs
