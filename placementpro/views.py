from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from students.models import Student, Application
from companies.models import Company
from django.contrib import messages


# 🔐 LOGIN
def login_view(request):

    if request.user.is_authenticated:

        if request.user.is_superuser or request.user.is_staff:
            return redirect('/dashboard/')

        elif Company.objects.filter(user=request.user).exists():
            return redirect('/companies/dashboard/')

        elif Student.objects.filter(user=request.user).exists():
            return redirect('/students/dashboard/')

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Please fill all fields")
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser or user.is_staff:
                return redirect('/dashboard/')

            elif Company.objects.filter(user=user).exists():
                return redirect('/companies/dashboard/')

            else:
                return redirect('/students/dashboard/')

        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')


# 📊 DASHBOARD
@login_required
def dashboard(request):

    if request.user.is_superuser or request.user.is_staff:

        students = Student.objects.count()
        companies = Company.objects.count()
        applications = Application.objects.count()

        selected = Application.objects.filter(status='Selected').count()
        rejected = Application.objects.filter(status='Rejected').count()
        pending = Application.objects.filter(status='Pending').count()

        return render(request, 'dashboard.html', {
            'students': students,        # ✅ FIXED (removed .count())
            'companies': companies,
            'applications': applications,
            'selected': selected,
            'rejected': rejected,
            'pending': pending,
        })

    elif Company.objects.filter(user=request.user).exists():
        return redirect('/companies/dashboard/')

    elif Student.objects.filter(user=request.user).exists():
        return redirect('/students/dashboard/')

    return redirect('/')


# 🚪 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('/login/')   


# 🏠 HOME
def home(request):

    if request.user.is_authenticated:

        if request.user.is_superuser or request.user.is_staff:
            return redirect('/dashboard/')

        elif Company.objects.filter(user=request.user).exists():
            return redirect('/companies/dashboard/')

        elif Student.objects.filter(user=request.user).exists():
            return redirect('/students/dashboard/')

    return render(request, 'home.html')