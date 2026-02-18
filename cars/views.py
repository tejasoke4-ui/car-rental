from django.shortcuts import render,redirect
from . models import Fleet,Register,Booking
from django.contrib.auth import authenticate,login as auth_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.db.models import Sum

def home(request):
     return render(request, 'index.html')

def fleet(request):
        flee=Fleet.objects.all()
        return render(request, 'fleet.html',{'flee':flee})


def cardetail(request, car_id):
    car = Fleet.objects.get(id=car_id)
    return render(request, 'cardetail.html', {'car': car})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def profile(request):
    if 'username' not in request.session:
        return redirect('login')

    user = Register.objects.get(username=request.session['username'])
    return render(request, 'profile.html', {'user': user})

def mybookings(request):
    if 'username' not in request.session:
        return redirect('login')

    user = Register.objects.get(username=request.session['username'])
    bookings = Booking.objects.filter(user=user).order_by('-start_date')
    return render(request, 'mybookings.html', {'bookings': bookings})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # First, try superuser login (Django auth_user)
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            auth_login(request, user)
            return redirect('admin_dashboard')  # go to admin dashboard

        # Else, try normal user login (custom Register table)
        try:
            reg_user = Register.objects.get(username=username)
            if check_password(password, reg_user.password):
                # Save username in session
                request.session['username'] = reg_user.username
                request.session['full_name'] = reg_user.full_name
                return redirect('dashboard')  # go to normal dashboard
            else:
                messages.error(request, "Incorrect password")
        except Register.DoesNotExist:
            messages.error(request, "Username not found")

    return render(request, "login.html")

def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if Register.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
        else:
            user = Register(full_name=full_name, username=username, password=password)
            user.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect("login")

    return render(request, "register.html")

def logout_view(request):
    if 'username' in request.session:
        del request.session['username']
        del request.session['full_name']
    django_logout(request)  # also logs out superuser if needed
    messages.success(request, "You have been logged out")
    return redirect('login')

def dashboard(request):
    # Make sure normal user is logged in
    if 'username' not in request.session:
        return redirect('login')

    total_cars = Fleet.objects.count()
    available_cars = Fleet.objects.filter(available=True).count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Recent bookings (latest 5)
    recent_bookings = Booking.objects.order_by('-start_date')[:5]

    # All cars for display
    fleet = Fleet.objects.all()

    context = {
        'full_name': request.session.get('full_name'),
        'total_cars': total_cars,
        'available_cars': available_cars,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'fleet': fleet,
    }
    return render(request, 'dashboard.html', context)

def bookings_view(request):
    # Fetch all bookings with related user and car info to avoid extra queries
    bookings = Booking.objects.select_related('user', 'car').all()
    return render(request, 'bookings.html', {'bookings': bookings})

def new_booking_view(request):
    # Later you can add form logic here
    if 'username' not in request.session:
        return redirect('login')

    if request.method == 'POST':
        user = Register.objects.get(username=request.session['username'])
        car_id = request.POST.get('car_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        car = Fleet.objects.get(id=car_id)
        # Simple calculation: days * price
        from datetime import datetime
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        days = (end - start).days
        total_price = days * car.price

        booking = Booking(
            user=user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price
        )
        booking.save()
        messages.success(request, 'Booking created successfully!')
        return redirect('mybookings')

    cars = Fleet.objects.filter(available=True)
    return render(request, 'new_booking.html', {'cars': cars})


def view_booking(request, booking_id):
    if 'username' not in request.session:
        return redirect('login')

    booking = Booking.objects.get(id=booking_id)
    user = Register.objects.get(username=request.session['username'])

    # Check if user owns this booking
    if booking.user != user:
        return redirect('dashboard')

    return render(request, 'view_booking.html', {'booking': booking})


def cancel_booking(request, booking_id):
    if 'username' not in request.session:
        return redirect('login')

    booking = Booking.objects.get(id=booking_id)
    user = Register.objects.get(username=request.session['username'])

    # Check if user owns this booking
    if booking.user != user:
        return redirect('dashboard')

    if request.method == 'POST':
        booking.status = 'Cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully!')
        return redirect('mybookings')

    return render(request, 'cancel_booking.html', {'booking': booking})


def users_view(request):
    if 'username' not in request.session:
        return redirect('login')

    users = Register.objects.all()
    return render(request, 'users.html', {'users': users})


# ========== ADMIN VIEWS ==========

def admin_login(request):
    """Admin login page"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Try admin/superuser login
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            auth_login(request, user)
            request.session['is_admin'] = True
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid admin credentials")

    return render(request, 'admin_login.html')


def admin_dashboard(request):
    """Admin dashboard with stats"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    total_cars = Fleet.objects.count()
    available_cars = Fleet.objects.filter(available=True).count()
    total_users = Register.objects.count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0

    recent_bookings = Booking.objects.order_by('-start_date')[:5]
    fleet = Fleet.objects.all()

    context = {
        'total_cars': total_cars,
        'available_cars': available_cars,
        'total_users': total_users,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'fleet': fleet,
        'admin_name': request.user.username,
    }
    return render(request, 'admin_dashboard.html', context)


def admin_cars(request):
    """List all cars"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    cars = Fleet.objects.all().order_by('-id')
    return render(request, 'admin_cars.html', {'cars': cars})


def admin_car_add(request):
    """Add new car"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    if request.method == 'POST':
        brand = request.POST.get('brand')
        car_model = request.POST.get('car_model')
        car_variant = request.POST.get('car_variant')
        category = request.POST.get('category')
        price = request.POST.get('price')
        available = request.POST.get('available') == 'on'
        img = request.FILES.get('img')

        car = Fleet(
            brand=brand,
            car_model=car_model,
            car_variant=car_variant,
            category=category,
            price=price,
            available=available,
            img=img
        )
        car.save()
        messages.success(request, f'{brand} {car_model} added successfully!')
        return redirect('admin_cars')

    return render(request, 'admin_car_form.html', {'action': 'Add'})


def admin_car_edit(request, car_id):
    """Edit existing car"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    car = Fleet.objects.get(id=car_id)

    if request.method == 'POST':
        car.brand = request.POST.get('brand')
        car.car_model = request.POST.get('car_model')
        car.car_variant = request.POST.get('car_variant')
        car.category = request.POST.get('category')
        car.price = request.POST.get('price')
        car.available = request.POST.get('available') == 'on'

        if request.FILES.get('img'):
            car.img = request.FILES.get('img')

        car.save()
        messages.success(request, f'{car.brand} {car.car_model} updated successfully!')
        return redirect('admin_cars')

    return render(request, 'admin_car_form.html', {'car': car, 'action': 'Edit'})


def admin_car_delete(request, car_id):
    """Delete car"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    car = Fleet.objects.get(id=car_id)

    if request.method == 'POST':
        car_name = f"{car.brand} {car.car_model}"
        car.delete()
        messages.success(request, f'{car_name} deleted successfully!')
        return redirect('admin_cars')

    return render(request, 'admin_car_delete.html', {'car': car})


def admin_bookings(request):
    """List all bookings"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    bookings = Booking.objects.select_related('user', 'car').order_by('-start_date')
    return render(request, 'admin_bookings.html', {'bookings': bookings})


def admin_booking_update(request, booking_id):
    """Update booking status"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    booking = Booking.objects.get(id=booking_id)

    if request.method == 'POST':
        booking.status = request.POST.get('status')
        booking.save()
        messages.success(request, 'Booking status updated!')
        return redirect('admin_bookings')

    return render(request, 'admin_booking_update.html', {'booking': booking})


def admin_users(request):
    """List all users"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    users = Register.objects.all().order_by('-id')
    return render(request, 'admin_users.html', {'users': users})


def admin_user_delete(request, user_id):
    """Delete user"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('admin_login')

    user = Register.objects.get(id=user_id)

    if request.method == 'POST':
        user.delete()
        messages.success(request, f'{user.username} deleted successfully!')
        return redirect('admin_users')

    return render(request, 'admin_user_delete.html', {'user': user})