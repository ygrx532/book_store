from django.db import models

# Customer model
class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True) 
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=10)
       
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['id']
