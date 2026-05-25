from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id',
            'title',
            'category',
            'description',
            'location',
            'reporter',
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

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return attrs

        user = request.user
        if request.method not in ['PUT', 'PATCH']:
            return attrs

        if getattr(user, 'is_admin', False):
            allowed_fields = {'status'}
            submitted_fields = set(attrs.keys())
            if not submitted_fields:
                raise serializers.ValidationError(
                    'Admin hanya dapat memperbarui status laporan.'
                )
            if not submitted_fields.issubset(allowed_fields):
                raise serializers.ValidationError(
                    'Admin hanya dapat memperbarui status laporan.'
                )
            return attrs

        if 'reporter' in attrs:
            raise serializers.ValidationError(
                'Reporter laporan tidak dapat diubah.'
            )

        return attrs
