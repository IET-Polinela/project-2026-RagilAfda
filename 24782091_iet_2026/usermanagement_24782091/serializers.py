from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email sudah terdaftar.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Konfirmasi password tidak cocok.'})

        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')

        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            is_admin=False,
            is_member=True,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
