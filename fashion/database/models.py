from django.db import models

# Create your models here.
class Product(models.Model):
    CATEGORY_CHOICES=[
        ("clothes","clothes"),
        ("footwear","footwear"),
        ("accessories","accessories"),
    ]
    title=models.CharField(max_length=250)
    category=models.CharField(max_length=20,choices=CATEGORY_CHOICES)
    sub_category = models.CharField(max_length=100)
    color = models.CharField(max_length=50, blank=True, null=True)
    description=models.TextField()
    size = models.CharField(max_length=10, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock=models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def __str__(self):
        return f"{self.sub_category} : {self.title}"