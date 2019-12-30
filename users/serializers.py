#  Copyright (c) Code Written and Tested by Ahmed Emad in 30/12/2019, 17:08
from django.contrib.auth.models import User
from rest_framework import serializers

from users.models import UserProfileModel, UserAddressModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class UserProfileSerializer(serializers.ModelSerializer):
    account = UserSerializer()

    class Meta:
        model = UserProfileModel
        fields = ('id', 'account', 'profile_photo', 'phone_number')
        extra_kwargs = {
            'id': {'read_only': True},
            'profile_photo': {'required': False},
            'phone_number': {'required': False}
        }

    def create(self, validated_data):
        user_data = validated_data.pop('account')
        user = User(**user_data)
        user.set_password(user.password)
        user.save()

        user_profile = UserProfileModel.objects.create(account=user, **validated_data)
        return user_profile

    def update(self, instance, validated_data):
        instance.profile_photo = validated_data.get('profile_photo', instance.profile_photo)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()

        user_data = validated_data.pop('account', {})
        account = instance.account
        account.first_name = user_data.get('first_name', account.first_name)
        account.last_name = user_data.get('last_name', account.last_name)
        account.save()

        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddressModel
        exclude = ('id', 'user')
        extra_kwargs = {
            'sort': {'read_only': True}
        }

    def create(self, validated_data):
        address = UserAddressModel(**validated_data)
        latest_sort = UserAddressModel.objects.filter(user=validated_data['user']).count()
        address.sort = latest_sort + 1
        address.save()
        return address
