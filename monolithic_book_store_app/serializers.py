# serializers.py
from rest_framework import serializers
from decimal import Decimal, InvalidOperation
from .models import Book, Customer
from django.core.validators import validate_email
import re


class ExactTwoDecimalField(serializers.DecimalField):
    def to_internal_value(self, data):
        # Raw string check before coercing to Decimal
        if not re.match(r'^\d+\.\d{2}$', str(data)):
            raise serializers.ValidationError("Price must be positive and have exactly 2 decimal places.")
        
        try:
            value = super().to_internal_value(data)
        except (InvalidOperation, ValueError):
            raise serializers.ValidationError("Invalid price format.")
        
        return value

class BookSerializer(serializers.ModelSerializer):
    price = ExactTwoDecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Book
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Convert price from string to float (optional)
        if 'price' in data:
            data['price'] = float(data['price'])
        return data

class CustomerSerializer(serializers.ModelSerializer):
    userId = serializers.EmailField()

    class Meta:
        model = Customer
        fields = '__all__'

    def validate_userId(self, value):
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Invalid email address.")
        return value
    
    def validate_state(self, value):
        if len(value) != 2 or not value.isalpha():
            raise serializers.ValidationError("State must be a valid 2-letter abbreviation.")
        return value
