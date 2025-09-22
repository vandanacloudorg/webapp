from rest_framework import serializers
from .models import User
from .models import Product

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'account_created', 'account_updated']
        read_only_fields = ['id', 'account_created', 'account_updated']

    def create(self, validated_data):
        # Use Django’s built-in password hashing
        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])  # hashes password
        user.save()
        return user

    def update(self, instance, validated_data):
        # Handle password hashing if provided
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)

class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')  # showing owner's email, not id

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'sku', 'manufacturer',
            'quantity', 'date_added', 'date_updated', 'owner'
        ]
        read_only_fields = ['id', 'date_added', 'date_updated', 'owner']
