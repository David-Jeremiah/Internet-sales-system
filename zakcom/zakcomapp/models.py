from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class InternetPackage(models.Model):
    name = models.CharField(max_length=100)
    speed = models.CharField(max_length=50)  # e.g., "10 Mbps", "50 Mbps"
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    installation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.speed}"


class Prospect(models.Model):
    """Potential customers that have been visited"""
    INTEREST_LEVEL_CHOICES = [
        ('very_interested', 'Very Interested'),
        ('interested', 'Interested'),
        ('neutral', 'Neutral'),
        ('not_interested', 'Not Interested'),
        ('converted', 'Converted to Customer'),
    ]

    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    location = models.CharField(max_length=200, help_text="Area/Estate/Building")

    interest_level = models.CharField(max_length=20, choices=INTEREST_LEVEL_CHOICES, default='neutral')
    preferred_package = models.ForeignKey(InternetPackage, on_delete=models.SET_NULL, null=True, blank=True)

    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prospects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.location}"


class Visit(models.Model):
    """Record of each visit made by sales team"""
    OUTCOME_CHOICES = [
        ('interested', 'Showed Interest'),
        ('not_interested', 'Not Interested'),
        ('follow_up', 'Needs Follow-up'),
        ('closed_sale', 'Closed Sale'),
        ('not_home', 'Not Home'),
        ('wrong_location', 'Wrong Location'),
    ]

    sales_person = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visits')
    prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE, related_name='visits', null=True, blank=True)

    visit_date = models.DateField(default=timezone.now)
    visit_time = models.TimeField(default=timezone.now)
    location = models.CharField(max_length=200, help_text="Area/Estate/Building visited")

    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)
    feedback = models.TextField(help_text="Customer feedback and comments")

    # Objections and concerns
    price_concern = models.BooleanField(default=False)
    coverage_concern = models.BooleanField(default=False)
    has_existing_provider = models.BooleanField(default=False)
    existing_provider_name = models.CharField(max_length=100, blank=True)

    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-visit_date', '-visit_time']

    def __str__(self):
        return f"{self.sales_person.username} - {self.location} - {self.visit_date}"


class Customer(models.Model):
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    id_number = models.CharField(max_length=50, blank=True)

    # Link to prospect if converted
    prospect = models.OneToOneField(Prospect, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class Sale(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('installed', 'Installed'),
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
    ]

    sales_person = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    package = models.ForeignKey(InternetPackage, on_delete=models.PROTECT)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sale_date = models.DateField(default=timezone.now)
    installation_date = models.DateField(blank=True, null=True)

    contract_duration = models.IntegerField(default=12)  # months
    total_value = models.DecimalField(max_digits=10, decimal_places=2)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.full_name} - {self.package.name}"

    def save(self, *args, **kwargs):
        if not self.total_value:
            self.total_value = (self.package.monthly_price * self.contract_duration) + self.package.installation_fee
        super().save(*args, **kwargs)


class SalesTarget(models.Model):
    sales_person = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    target_count = models.IntegerField()
    target_visits = models.IntegerField(default=0)  # Target number of visits
    achieved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    achieved_count = models.IntegerField(default=0)
    achieved_visits = models.IntegerField(default=0)

    class Meta:
        unique_together = ['sales_person', 'month']

    def __str__(self):
        return f"{self.sales_person.username} - {self.month.strftime('%B %Y')}"
