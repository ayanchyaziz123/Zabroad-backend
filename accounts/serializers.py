from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile


class RegisterSerializer(serializers.ModelSerializer):
    password     = serializers.CharField(write_only=True, min_length=8)
    handle       = serializers.CharField(max_length=50)
    home_country = serializers.CharField(default='Bangladesh')
    country_flag = serializers.CharField(default='🇧🇩')
    lives_in     = serializers.CharField(default='Queens, NY')
    visa_status  = serializers.CharField(default='OPT')

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'password',
                  'handle', 'home_country', 'country_flag', 'lives_in', 'visa_status']

    def validate_handle(self, value):
        if Profile.objects.filter(handle=value).exists():
            raise serializers.ValidationError('Handle already taken.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value

    def create(self, validated_data):
        profile_fields = {
            k: validated_data.pop(k)
            for k in ['handle', 'home_country', 'country_flag', 'lives_in', 'visa_status']
        }
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.username = profile_fields['handle'].lstrip('@')
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user, **profile_fields)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Profile
        fields = ['handle', 'avatar_emoji', 'home_country', 'country_flag',
                  'lives_in', 'visa_status', 'bio']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    name    = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'name', 'email', 'profile']

    def get_name(self, obj):
        return obj.get_full_name() or obj.username
