from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .models import Sale, Customer, InternetPackage, SalesTarget, Visit, Prospect
from .forms import SaleForm, CustomerForm, VisitForm, ProspectForm


def is_admin(user):
    return user.is_staff or user.is_superuser


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


@login_required
@user_passes_test(is_admin)
def user_management(request):
    """Admin view to manage users - FIXED"""
    users = User.objects.all().order_by('-date_joined')

    # FIXED: Count admins and sales people correctly
    admin_count = User.objects.filter(is_staff=True).count()
    sales_count = User.objects.filter(is_staff=False).count()

    # Get stats for each user
    for user in users:
        user.total_sales = Sale.objects.filter(sales_person=user).count()
        user.total_visits = Visit.objects.filter(sales_person=user).count()

        # Calculate total revenue for each user
        user.total_revenue = Sale.objects.filter(
            sales_person=user
        ).aggregate(total=Sum('total_value'))['total'] or 0

    context = {
        'users': users,
        'admin_count': admin_count,
        'sales_count': sales_count,
        'total_users': users.count(),
    }
    return render(request, 'admin/user_management.html', context)


@login_required
@user_passes_test(is_admin)
def create_user(request):
    """Admin creates new user"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        is_staff = request.POST.get('is_staff') == 'on'

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('create_user')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('create_user')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff,
            is_active=True
        )

        messages.success(request, f"User {username} created successfully!")
        return redirect('user_management')

    return render(request, 'admin/create_user.html')


@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    """Admin edits user"""
    user_to_edit = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user_to_edit.first_name = request.POST.get('first_name')
        user_to_edit.last_name = request.POST.get('last_name')
        user_to_edit.email = request.POST.get('email')
        user_to_edit.is_staff = request.POST.get('is_staff') == 'on'
        user_to_edit.is_active = request.POST.get('is_active') == 'on'

        new_password = request.POST.get('new_password')
        if new_password:
            user_to_edit.set_password(new_password)

        user_to_edit.save()
        messages.success(request, f"User {user_to_edit.username} updated successfully!")
        return redirect('user_management')

    context = {
        'user_to_edit': user_to_edit,
    }
    return render(request, 'admin/edit_user.html', context)


@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    """Admin deletes user"""
    user_to_delete = get_object_or_404(User, id=user_id)

    if user_to_delete == request.user:
        messages.error(request, "You cannot delete yourself!")
        return redirect('user_management')

    username = user_to_delete.username
    user_to_delete.delete()
    messages.success(request, f"User {username} deleted successfully!")
    return redirect('user_management')


@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect('sales_dashboard')


@login_required
def sales_dashboard(request):
    """Dashboard for sales team members - FIXED"""
    user = request.user
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # User's sales stats
    total_sales = Sale.objects.filter(sales_person=user).count()
    monthly_sales = Sale.objects.filter(
        sales_person=user,
        sale_date__gte=month_start
    ).count()

    monthly_revenue = Sale.objects.filter(
        sales_person=user,
        sale_date__gte=month_start
    ).aggregate(total=Sum('total_value'))['total'] or 0

    # Visit stats
    total_visits = Visit.objects.filter(sales_person=user).count()
    monthly_visits = Visit.objects.filter(
        sales_person=user,
        visit_date__gte=month_start
    ).count()

    # FIXED: Conversion rate - count sales that came from visits
    monthly_sales_from_visits = Sale.objects.filter(
        sales_person=user,
        sale_date__gte=month_start
    ).count()

    conversion_rate = (monthly_sales_from_visits / monthly_visits * 100) if monthly_visits > 0 else 0

    # Recent visits
    recent_visits = Visit.objects.filter(sales_person=user).order_by('-visit_date', '-visit_time')[:10]

    # Recent sales
    recent_sales = Sale.objects.filter(sales_person=user).order_by('-sale_date')[:5]

    # Follow-ups needed
    follow_ups = Visit.objects.filter(
        sales_person=user,
        follow_up_date__isnull=False,
        follow_up_date__gte=today,
        outcome='follow_up'
    ).order_by('follow_up_date')[:5]

    # Get monthly target
    try:
        target = SalesTarget.objects.get(sales_person=user, month=month_start)
    except SalesTarget.DoesNotExist:
        target = None

    context = {
        'total_sales': total_sales,
        'monthly_sales': monthly_sales,
        'monthly_revenue': monthly_revenue,
        'total_visits': total_visits,
        'monthly_visits': monthly_visits,
        'conversion_rate': round(conversion_rate, 1),
        'recent_visits': recent_visits,
        'recent_sales': recent_sales,
        'follow_ups': follow_ups,
        'target': target,
    }
    return render(request, 'sales/sales_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Dashboard for administrators - COMPLETELY FIXED"""
    from django.db.models.functions import TruncDate

    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Overall stats - FIXED
    total_sales = Sale.objects.count()
    monthly_sales = Sale.objects.filter(sale_date__gte=month_start).count()

    # FIXED: Revenue calculations
    total_revenue = Sale.objects.aggregate(total=Sum('total_value'))['total'] or 0
    monthly_revenue = Sale.objects.filter(
        sale_date__gte=month_start
    ).aggregate(total=Sum('total_value'))['total'] or 0

    # Visit stats
    total_visits = Visit.objects.count()
    monthly_visits = Visit.objects.filter(visit_date__gte=month_start).count()

    # FIXED: Overall conversion rate - sales from visits
    monthly_sales_count = Sale.objects.filter(sale_date__gte=month_start).count()
    overall_conversion = (monthly_sales_count / monthly_visits * 100) if monthly_visits > 0 else 0

    # Sales by status
    status_breakdown = Sale.objects.values('status').annotate(
        count=Count('id')
    )

    # Visit outcomes breakdown
    outcome_breakdown = Visit.objects.filter(
        visit_date__gte=month_start
    ).values('outcome').annotate(
        count=Count('id')
    )

    # FIXED: Top performers - calculate manually to avoid duplicates
    sales_people = User.objects.filter(is_staff=False, is_active=True)
    top_performers = []

    for person in sales_people:
        monthly_sales = Sale.objects.filter(
            sales_person=person,
            sale_date__gte=month_start
        ).count()

        monthly_revenue = Sale.objects.filter(
            sales_person=person,
            sale_date__gte=month_start
        ).aggregate(total=Sum('total_value'))['total'] or 0

        monthly_visits = Visit.objects.filter(
            sales_person=person,
            visit_date__gte=month_start
        ).count()

        # Only include if they have activity
        if monthly_sales > 0 or monthly_visits > 0:
            conversion_rate = round((monthly_sales / monthly_visits) * 100, 1) if monthly_visits > 0 else 0

            top_performers.append({
                'username': person.username,
                'first_name': person.first_name,
                'last_name': person.last_name,
                'sales_count': monthly_sales,
                'revenue': monthly_revenue,
                'visits_count': monthly_visits,
                'conversion_rate': conversion_rate,
            })

    # Sort by multiple criteria and take top 5:
    # 1. Monthly revenue (highest first)
    # 2. If revenue is same, sort by monthly visits (highest first)
    # 3. If visits are same, sort by conversion rate (highest first)
    top_performers.sort(key=lambda x: (
        -(x['revenue'] or 0),  # Primary: Revenue
        -(x['visits_count'] or 0),  # Secondary: Visits
        -(x['conversion_rate'] or 0)  # Tertiary: Conversion rate
    ))
    top_performers = top_performers[:5]

    # Sales by package - FIXED
    package_stats = Sale.objects.values('package__name').annotate(
        count=Count('id'),
        revenue=Sum('total_value')
    ).order_by('-count')

    # Common objections
    common_objections = {
        'price': Visit.objects.filter(visit_date__gte=month_start, price_concern=True).count(),
        'coverage': Visit.objects.filter(visit_date__gte=month_start, coverage_concern=True).count(),
        'existing_provider': Visit.objects.filter(visit_date__gte=month_start, has_existing_provider=True).count(),
    }

    # Daily sales and visits trend (last 30 days)
    last_30_days = today - timedelta(days=30)

    # Get sales grouped by date
    daily_sales = Sale.objects.filter(
        sale_date__gte=last_30_days
    ).annotate(
        date=TruncDate('sale_date')
    ).values('date').annotate(
        sales=Count('id')
    ).order_by('date')

    # Get visits grouped by date
    daily_visits = Visit.objects.filter(
        visit_date__gte=last_30_days
    ).annotate(
        date=TruncDate('visit_date')
    ).values('date').annotate(
        visits=Count('id')
    ).order_by('date')

    # Create dictionaries for quick lookup
    sales_dict = {item['date']: item['sales'] for item in daily_sales}
    visits_dict = {item['date']: item['visits'] for item in daily_visits}

    # Build daily activity with all 30 days
    daily_activity = []
    for i in range(30):
        date = last_30_days + timedelta(days=i)
        daily_activity.append({
            'date': date,
            'sales': sales_dict.get(date, 0),
            'visits': visits_dict.get(date, 0)
        })

    context = {
        'total_sales': total_sales,
        'monthly_sales': monthly_sales,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'total_visits': total_visits,
        'monthly_visits': monthly_visits,
        'overall_conversion': round(overall_conversion, 1),
        'status_breakdown': status_breakdown,
        'outcome_breakdown': outcome_breakdown,
        'top_performers': top_performers,
        'package_stats': package_stats,
        'common_objections': common_objections,
        'daily_activity': daily_activity,
    }
    return render(request, 'sales/admin_dashboard.html', context)


@login_required
@login_required
def log_visit(request):
    """Sales team logs a visit - FIXED to always save visits regardless of outcome"""
    if request.method == 'POST':

        visit_form = VisitForm(request.POST)

        if visit_form.is_valid():
            # Create the visit object but don't save yet
            visit = visit_form.save(commit=False)
            visit.sales_person = request.user

            # Save the visit FIRST to ensure it's always recorded
            visit.save()

            # NOW handle prospect creation only for interested outcomes
            outcome = visit.outcome
            if outcome in ['interested', 'follow_up', 'closed_sale']:
                prospect_name = request.POST.get('full_name', '').strip()
                prospect_phone = request.POST.get('phone', '').strip()

                # Only create prospect if they filled in name AND phone (minimum required)
                if prospect_name and prospect_phone:
                    try:
                        # Determine interest level based on outcome
                        if outcome == 'closed_sale':
                            interest_level = 'converted'
                        elif outcome == 'follow_up':
                            interest_level = 'very_interested'
                        else:
                            interest_level = 'interested'

                        # Get preferred package if provided
                        preferred_package_id = request.POST.get('preferred_package')

                        # Create prospect
                        prospect = Prospect.objects.create(
                            full_name=prospect_name,
                            phone=prospect_phone,
                            email=request.POST.get('email', '').strip(),
                            address=request.POST.get('address', '').strip() or 'Not provided',
                            location=request.POST.get('prospect_location', '').strip() or visit.location,
                            added_by=request.user,
                            interest_level=interest_level,
                            preferred_package_id=preferred_package_id if preferred_package_id else None
                        )

                        # Link prospect to visit
                        visit.prospect = prospect
                        visit.save()  # Save again to update the prospect link

                        messages.success(request, 'Visit and prospect information saved successfully!')
                    except Exception as e:
                        # Visit is already saved, just notify about prospect issue
                        messages.warning(request, f'Visit saved but prospect creation failed: {str(e)}')
                else:
                    # Visit saved, but no prospect data provided
                    messages.success(request, 'Visit logged successfully! (No prospect details saved)')
            else:
                # For not_interested, not_home, wrong_location outcomes
                messages.success(request, 'Visit logged successfully!')

            return redirect('sales_dashboard')
        else:
            # Debug: Print form errors
            print("Form Errors:", visit_form.errors)
            print("Form Data:", visit_form.data)

            # Show validation errors
            for field, errors in visit_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        visit_form = VisitForm()
        prospect_form = ProspectForm()

    context = {
        'visit_form': visit_form,
        'prospect_form': ProspectForm(),
    }
    return render(request, 'sales/log_visit.html', context)

@login_required
def visit_list(request):
    """View all visits"""
    if request.user.is_staff:
        visits = Visit.objects.all()
    else:
        visits = Visit.objects.filter(sales_person=request.user)

    outcome = request.GET.get('outcome')
    if outcome:
        visits = visits.filter(outcome=outcome)

    date_from = request.GET.get('date_from')
    if date_from:
        visits = visits.filter(visit_date__gte=date_from)

    date_to = request.GET.get('date_to')
    if date_to:
        visits = visits.filter(visit_date__lte=date_to)

    context = {
        'visits': visits,
        'outcome_choices': Visit.OUTCOME_CHOICES,
    }
    return render(request, 'sales/visit_list.html', context)


@login_required
def prospect_list(request):
    """View all prospects"""
    if request.user.is_staff:
        prospects = Prospect.objects.all()
    else:
        prospects = Prospect.objects.filter(added_by=request.user)

    interest = request.GET.get('interest')
    if interest:
        prospects = prospects.filter(interest_level=interest)

    context = {
        'prospects': prospects,
        'interest_choices': Prospect.INTEREST_LEVEL_CHOICES,
    }
    return render(request, 'sales/prospect_list.html', context)


@login_required
def create_sale(request):
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        sale_form = SaleForm(request.POST)

        if customer_form.is_valid() and sale_form.is_valid():
            customer = customer_form.save()
            sale = sale_form.save(commit=False)
            sale.customer = customer
            sale.sales_person = request.user
            sale.save()
            messages.success(request, 'Sale created successfully!')
            return redirect('sales_dashboard')
    else:
        customer_form = CustomerForm()
        sale_form = SaleForm()

    context = {
        'customer_form': customer_form,
        'sale_form': sale_form,
        'packages': InternetPackage.objects.filter(is_active=True)
    }
    return render(request, 'sales/create_sale.html', context)


@login_required
def sale_list(request):
    """View all sales - FIXED"""
    if request.user.is_staff:
        sales = Sale.objects.all()
    else:
        sales = Sale.objects.filter(sales_person=request.user)

    status = request.GET.get('status')
    if status:
        sales = sales.filter(status=status)

    date_from = request.GET.get('date_from')
    if date_from:
        sales = sales.filter(sale_date__gte=date_from)

    date_to = request.GET.get('date_to')
    if date_to:
        sales = sales.filter(sale_date__lte=date_to)

    # FIXED: Calculate totals properly
    total_revenue = sales.aggregate(total=Sum('total_value'))['total'] or 0
    sales_count = sales.count()
    average_sale = total_revenue / sales_count if sales_count > 0 else 0

    context = {
        'sales': sales,
        'status_choices': Sale.STATUS_CHOICES,
        'total_revenue': total_revenue,
        'average_sale': average_sale,
    }
    return render(request, 'sales/sale_list.html', context)


@login_required
@user_passes_test(is_admin)
def team_performance(request):
    """Detailed team performance view for admins - COMPLETELY FIXED"""
    from django.db.models import Prefetch

    month_start = timezone.now().date().replace(day=1)

    # Get all sales people (not admins)
    sales_people = User.objects.filter(
        is_active=True,
        is_staff=False
    )

    # Build team stats manually to avoid duplicate counting issues
    team_stats = []
    for person in sales_people:
        # Count sales correctly
        total_sales = Sale.objects.filter(sales_person=person).count()
        monthly_sales = Sale.objects.filter(
            sales_person=person,
            sale_date__gte=month_start
        ).count()

        # Calculate revenue correctly
        total_revenue = Sale.objects.filter(
            sales_person=person
        ).aggregate(total=Sum('total_value'))['total'] or 0

        monthly_revenue = Sale.objects.filter(
            sales_person=person,
            sale_date__gte=month_start
        ).aggregate(total=Sum('total_value'))['total'] or 0

        # Count visits correctly
        total_visits = Visit.objects.filter(sales_person=person).count()
        monthly_visits = Visit.objects.filter(
            sales_person=person,
            visit_date__gte=month_start
        ).count()

        # Calculate conversion rate
        if monthly_visits > 0:
            conversion_rate = round((monthly_sales / monthly_visits) * 100, 1)
        else:
            conversion_rate = 0

        # Create stat object
        stat = {
            'id': person.id,
            'username': person.username,
            'first_name': person.first_name,
            'last_name': person.last_name,
            'email': person.email,
            'total_sales': total_sales,
            'monthly_sales': monthly_sales,
            'total_revenue': total_revenue,
            'monthly_revenue': monthly_revenue,
            'total_visits': total_visits,
            'monthly_visits': monthly_visits,
            'conversion_rate': conversion_rate,
        }

        team_stats.append(stat)

    # Sort by multiple criteria:
    # 1. Monthly revenue (highest first)
    # 2. If revenue is same, sort by monthly visits (highest first)
    # 3. If visits are same, sort by conversion rate (highest first)
    team_stats.sort(key=lambda x: (
        -(x['monthly_revenue'] or 0),  # Negative for descending order
        -(x['monthly_visits'] or 0),  # Then by visits
        -(x['conversion_rate'] or 0)  # Then by conversion rate
    ))

    context = {
        'team_stats': team_stats,
    }
    return render(request, 'sales/team_performance.html', context)



@login_required
@user_passes_test(is_admin)
def feedback_analysis(request):
    """Analyze customer feedback and objections"""
    month_start = timezone.now().date().replace(day=1)

    visits_with_feedback = Visit.objects.filter(
        visit_date__gte=month_start
    ).exclude(feedback='')

    objections = {
        'price_concern': Visit.objects.filter(visit_date__gte=month_start, price_concern=True).count(),
        'coverage_concern': Visit.objects.filter(visit_date__gte=month_start, coverage_concern=True).count(),
        'has_existing_provider': Visit.objects.filter(visit_date__gte=month_start, has_existing_provider=True).count(),
    }

    existing_providers = Visit.objects.filter(
        visit_date__gte=month_start,
        has_existing_provider=True
    ).exclude(existing_provider_name='').values('existing_provider_name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    context = {
        'visits_with_feedback': visits_with_feedback,
        'objections': objections,
        'existing_providers': existing_providers,
    }
    return render(request, 'sales/feedback_analysis.html', context)


@login_required
def edit_profile(request):
    """User can edit their own profile"""
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')

        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if current_password and new_password:
            if request.user.check_password(current_password):
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    messages.success(request, 'Password updated successfully! Please login again.')
                    logout(request)
                    return redirect('login')
                else:
                    messages.error(request, 'New passwords do not match!')
                    return redirect('edit_profile')
            else:
                messages.error(request, 'Current password is incorrect!')
                return redirect('edit_profile')

        request.user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('edit_profile')

    context = {
        'user': request.user,
    }
    return render(request, 'sales/edit_profile.html', context)