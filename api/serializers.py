from rest_framework import serializers
from .models import User
from .models import Product

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [ 'id', 'email', 'first_name', 'last_name', 'password', 'account_created', 'account_updated']
        read_only_fields = ['id', 'account_created', 'account_updated']
        extra_kwargs = { 'email': {'required': True}, 'password': {'required': True},'first_name': {'required': True}, 'last_name': {'required': True}, }


    def create(self, validated_data):
        email = validated_data.get("email")
        password = validated_data.pop("password", None)

        if not email:
            raise serializers.ValidationError({"email": "This field is required."})
        if not password:
            raise serializers.ValidationError({"password": "This field is required."})

        user = User(
            email=email,
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )
        user.set_password(password)   # ✅ always hash password
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

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be less than 0.")
        return value

    def validate_sku(self, value):
        if Product.objects.filter(sku=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("SKU must be unique.")
        return value
