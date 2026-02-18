from django.db import models
from django.contrib.auth.hashers import make_password
class Fleet(models.Model):
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    car_model = models.CharField(max_length=100)
    img = models.ImageField(upload_to='pics/')
    price = models.IntegerField()
    car_variant = models.CharField(max_length=100)
    available = models.BooleanField(default=True)



class Register(models.Model):
    full_name = models.CharField(max_length=150)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # hash password if it's not already hashed
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    
class Booking(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    car = models.ForeignKey(Fleet, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.IntegerField()
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

