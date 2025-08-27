# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username', 'first_name', 'last_name')
        read_only_fields = ('id',)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('این ایمیل از قبل وجود دارد.')
        return value
    
    def validate_username(self, value):
        if value is None or value == '':
            return value
        # به صورت Case-insensitive
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('این نام‌کاربری قبلاً گرفته شده است.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # ایمیل یا نام‌کاربری
    password = serializers.CharField()