from django.db import models
from django.core.validators import RegexValidator

sku_validator = RegexValidator(
    regex=r'^[A-Z]{3}-\d{4}$',
    message='SKU must be in the format ABC-1234 (3 uppercase letters, hyphen, 4 digits).'
)

# Create your models here.
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    sku = models.CharField(
        max_length=50,
        unique=True,
        validators=[sku_validator],
        help_text='Format: ABC-1234 (3 uppercase letters, hyphen, 4 digits)'
    )
    price = models.FloatField()
    quantity = models.IntegerField()
    supplier = models.CharField(max_length=100)

    def __str__(self):
        return self.name