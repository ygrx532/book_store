# serializers.py
from rest_framework import serializers
from decimal import Decimal, InvalidOperation
from .models import Book, Customer
from django.core.validators import validate_email
import re

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