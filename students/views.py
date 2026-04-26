from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
import openpyxl
import re
from django.contrib import messages
from .models import Student, Application, Notification
from companies.models import Company, Job
from django.contrib.auth.decorators import login_required


# 🔹 STAFF CHECK
def is_staff(user):
    return user.is_staff


# 🔹 STUDENT LIST
@login_required
@user_passes_test(is_staff)
def student_list(request):
    students = Student.objects.all()
    return render(request, 'students/student_list.html', {'students': students})


# 🔹 ADD STUDENT
@login_required
@user_passes_test(is_staff)
def add_student(request):
    if request.method == 'POST':
        Student.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            cgpa=request.POST.get('cgpa'),
            resume=request.FILES.get('resume')
        )
        return redirect('/students/')
    return render(request, 'students/add_student.html')


# 🔹 EDIT STUDENT
@login_required
@user_passes_test(is_staff)
def edit_student(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        student.name = request.POST.get('name')
        student.email = request.POST.get('email')
        student.cgpa = request.POST.get('cgpa')

        if request.FILES.get('resume'):
            student.resume = request.FILES.get('resume')

        student.save()
        return redirect('/students/')

    return render(request, 'students/edit_student.html', {'student': student})


# 🔹 DELETE STUDENT
@login_required
@user_passes_test(is_staff)
def delete_student(request, id):
    student = get_object_or_404(Student, id=id)
    student.delete()
    return redirect('/students/')


# 🔹 APPLY COMPANY
@login_required
def apply_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    # ADMIN APPLY
    if request.user.is_superuser:
        students = Student.objects.all()

        if request.method == "POST":
            student_id = request.POST.get("student_id")
            student = get_object_or_404(Student, id=student_id)

            if student.cgpa < company.min_cgpa:
                return render(request, 'students/admin_apply.html', {
                    'company': company,
                    'students': students,
                    'error': "Low CGPA"
                })

            Application.objects.get_or_create(student=student, company=company)

            return redirect('/students/applications/')

        return render(request, 'students/admin_apply.html', {
            'company': company,
            'students': students
        })

    # STUDENT APPLY
    student = Student.objects.filter(user=request.user).first()

    if not student:
        return redirect('/')

    if student.cgpa < company.min_cgpa:
        return redirect('/companies/')

    Application.objects.get_or_create(student=student, company=company)

    return redirect('/students/applications/')


# 🔹 APPLICATION LIST
@login_required
def applications(request):
    if request.user.is_staff:
        apps = Application.objects.all()
    else:
        student = Student.objects.filter(user=request.user).first()
        apps = Application.objects.filter(student=student)

    return render(request, 'students/applications.html', {
        'applications': apps
    })


# 🔹 CANCEL APPLICATION
@login_required
def cancel_application(request, id):
    app = get_object_or_404(Application, id=id)

    if request.user.is_staff or app.student.user == request.user:
        app.delete()

    return redirect('/students/applications/')


# 🔹 STUDENT DASHBOARD
@login_required
def student_dashboard(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        return redirect('/')

    applications = Application.objects.filter(student=student)
    companies = Company.objects.all()

    total_apps = applications.count()
    eligible_companies = companies.filter(min_cgpa__lte=student.cgpa).count()

    selected = applications.filter(status='Selected').count()
    rejected = applications.filter(status='Rejected').count()

    return render(request, 'students/student_dashboard.html', {
        'student': student,
        'applications': applications,
        'total_apps': total_apps,
        'eligible_companies': eligible_companies,
        'selected': selected,
        'rejected': rejected
    })


# 🔥 RESUME ANALYSIS (IMPROVED AI-LIKE)
@login_required
def resume_analysis(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if not student.resume:
        return render(request, 'students/resume_result.html', {
            'error': 'No resume uploaded'
        })

    try:
        content = student.resume.read().decode('utf-8', errors='ignore').lower()
    except:
        content = ""

    score = 100
    issues = []
    good_points = []

    if re.search(r'\S+@\S+\.\S+', content):
        good_points.append("✅ Email found")
    else:
        issues.append("❌ Missing email")
        score -= 10

    if re.search(r'\d{10}', content):
        good_points.append("✅ Phone number found")
    else:
        issues.append("❌ Missing phone")
        score -= 10

    skills = ["python", "sql", "django", "excel", "java", "html", "css"]
    found = [s for s in skills if s in content]

    if len(found) >= 4:
        good_points.append("🔥 Strong skill section")
    elif len(found) > 0:
        issues.append("⚠ Add more technical skills")
        score -= 10
    else:
        issues.append("❌ No skills detected")
        score -= 20

    if "project" not in content:
        issues.append("⚠ Add projects section")
        score -= 10

    if score < 0:
        score = 0

    return render(request, 'students/resume_result.html', {
        'score': score,
        'issues': issues,
        'good_points': good_points
    })


# 🔹 DOWNLOAD EXCEL
@login_required
def download_students(request):
    wb = openpyxl.Workbook()
    ws = wb.active

    ws.append(['Name', 'Email', 'CGPA'])

    for s in Student.objects.all():
        ws.append([s.name, s.email, s.cgpa])

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=students.xlsx'
    wb.save(response)

    return response


# 🔹 NOTIFICATIONS
@login_required
def add_notification(request):

    if not request.user.is_superuser:
        return redirect('/students/notifications/')

    if request.method == "POST":
        message = request.POST.get('message')

        if message:
            Notification.objects.create(message=message)

        
            return redirect('/students/notifications/')

    return render(request, 'students/add_notification.html')

@login_required
def view_notifications(request):
    notes = Notification.objects.all().order_by('-id')  # latest first
    return render(request, 'students/notifications.html', {'notes': notes})

@login_required
def delete_notification(request, id):
    if not request.user.is_superuser:
        return redirect('/students/notifications/')  

    Notification.objects.filter(id=id).delete()
    return redirect('/students/notifications/')


# 🔹 APPLY JOB (FIXED)
@login_required
def apply_job(request, job_id):
    student = get_object_or_404(Student, user=request.user)
    job = get_object_or_404(Job, id=job_id)

    # ❌ prevent duplicate
    if Application.objects.filter(student=student, job=job).exists():
        return redirect('home')

    # ❌ eligibility check (important!)
    if student.cgpa < job.min_cgpa:
        return redirect('home')

    Application.objects.create(
        student=student,
        job=job,
        company=job.company,
        status="Pending"
    )

    return redirect('home')


@login_required
def admin_apply_job(request, job_id):
    
      # 🔒 THIS IS THE BONUS LINE
    if not request.user.is_superuser:
        return redirect('home')
    
    from students.models import Student, Application
    from companies.models import Job

    job = get_object_or_404(Job, id=job_id)
    students = Student.objects.all()

    if request.method == "POST":
        student_id = request.POST.get("student_id")
        student = get_object_or_404(Student, id=student_id)

        # ❌ eligibility check
        if student.cgpa < job.min_cgpa:
            return redirect('/companies/')

        # ❌ prevent duplicate
        if Application.objects.filter(student=student, job=job).exists():
            return redirect('/companies/')

        Application.objects.create(
            student=student,
            job=job,
            company=job.company,
            status="Pending"
        )

        return redirect('/companies/')

    return render(request, 'students/admin_apply_job.html', {
        'students': students,
        'job': job
    })