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
