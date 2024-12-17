from django.db import models

# Create your models here.

class Holiday(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    description = models.TextField()
    country = models.CharField(max_length=2)
    year = models.PositiveIntegerField()

    def __str__(self):
        return self.name