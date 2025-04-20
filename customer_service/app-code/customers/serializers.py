from rest_framework import serializers
from .models import Customer
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError

class CustomerSerializer(serializers.ModelSerializer):
    userId = serializers.EmailField()

    class Meta:
        model = Customer
        fields = '__all__'
    
    def validate_state(self, value):
        if len(value) != 2 or not value.isalpha():
            raise serializers.ValidationError("State must be a valid 2-letter abbreviation.")
        return value