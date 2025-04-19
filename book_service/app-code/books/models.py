from django.db import models

# Book model
class Book(models.Model):
    ISBN = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=255)
    Author = models.CharField(max_length=255)
    description = models.TextField()
    genre = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['ISBN']