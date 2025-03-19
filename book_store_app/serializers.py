# serializers.py
import re
from rest_framework import serializers
from decimal import Decimal, InvalidOperation
from .models import Book, Customer

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
    
    def validate_pric(self, value):
        try:
            print(type(value))
            if re.match(r'^\d+\.\d{2}$', str(value)) is None:
                raise serializers.ValidationError("Price must have exactly 2 decimal places.")
        except (InvalidOperation, ValueError):
            raise serializers.ValidationError("Invalid price format.")
        return value

class CustomerSerializer(serializers.ModelSerializer):
    userId = serializers.EmailField()

    class Meta:
        model = Customer
        fields = '__all__'
    
    def validate_state(self, value):
        if len(value) != 2 or not value.isalpha():
            raise serializers.ValidationError("State must be a valid 2-letter abbreviation.")
        return value
