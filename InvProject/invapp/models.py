from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

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


class AuditLog(models.Model):
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    ACTION_CHOICES = [
        (ACTION_CREATE, 'Create'),
        (ACTION_UPDATE, 'Update'),
        (ACTION_DELETE, 'Delete'),
    ]

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    product_id = models.IntegerField(null=True, blank=True)
    product_name = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    username = models.CharField(max_length=150, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(default=dict, blank=True)
    product_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} on {self.product_name or self.product_id} by {self.username} at {self.timestamp}"