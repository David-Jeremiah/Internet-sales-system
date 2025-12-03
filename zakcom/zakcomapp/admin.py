from django.contrib import admin
from .models import InternetPackage, Customer, Sale, SalesTarget, Visit, Prospect

@admin.register(InternetPackage)
class InternetPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'speed', 'monthly_price', 'installation_fee', 'is_active']
    list_filter = ['is_active']

@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'location', 'interest_level', 'added_by', 'created_at']
    list_filter = ['interest_level', 'added_by']
    search_fields = ['full_name', 'phone', 'location']

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ['sales_person', 'location', 'visit_date', 'outcome', 'prospect']
    list_filter = ['outcome', 'visit_date', 'price_concern', 'coverage_concern', 'has_existing_provider']
    search_fields = ['location', 'sales_person__username', 'feedback']
    date_hierarchy = 'visit_date'

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'created_at']
    search_fields = ['full_name', 'phone', 'email']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['customer', 'sales_person', 'package', 'status', 'total_value', 'sale_date']
    list_filter = ['status', 'sale_date', 'package']
    search_fields = ['customer__full_name', 'sales_person__username']
    date_hierarchy = 'sale_date'

@admin.register(SalesTarget)
class SalesTargetAdmin(admin.ModelAdmin):
    list_display = ['sales_person', 'month', 'target_amount', 'target_count', 'target_visits',
                    'achieved_amount', 'achieved_count', 'achieved_visits']
    list_filter = ['month']


# ============================================
# CUSTOM ADMIN SITE CONFIGURATION
# ============================================
admin.site.site_header = "Zakcom Telecom Administration"
admin.site.site_title = "Zakcom  Admin Portal"
admin.site.index_title = "Welcome to Zakcom Admin"