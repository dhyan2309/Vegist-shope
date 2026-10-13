from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.IntegerField(default=10, help_text="Percentage off, e.g. 20 for 20%")
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"

    def is_valid(self):
        now = timezone.now()
        if not self.active:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        return True
