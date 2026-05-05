from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
import openpyxl
import re
from django.contrib import messages
from .models import Student, Application, Notification
from companies.models import Company, Job
from django.contrib.auth.models import User
from django.http import FileResponse


# 🔹 STAFF CHECK
def is_staff(user):
    return user.is_staff


# 🔹 STUDENT LIST
@login_required
@user_passes_test(is_staff)
def student_list(request):
    query = request.GET.get('q')
    students = Student.objects.all()

    if query:
        students = students.filter(name__icontains=query)

    return render(request, 'students/student_list.html', {
        'students': students
    })
# 🔹 ADD STUDENT
@login_required
@user_passes_test(is_staff)
def add_student(request):
    if request.method == 'POST':

        username = request.POST.get('email')  # using email as username
        password = "123456"  # default password

        user = User.objects.create_user(
            username=username,
            password=password,
            email=request.POST.get('email')  # ✅ IMPORTANT
        )

        Student.objects.create(
            user=user,
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

        # ✅ UPDATE USER EMAIL (VERY IMPORTANT FOR RESET)
        if student.user:
            student.user.email = student.email
            student.user.username = student.email
            student.user.save()

        # ✅ RESUME FIX
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

    # delete linked user also
    if student.user:
        student.user.delete()

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
                messages.error(request, "Low CGPA")
                return redirect('/companies/')

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


    notes = Notification.objects.all().order_by('-id')[:5]

    return render(request, 'students/student_dashboard.html', {
        'student': student,
        'applications': applications,
        'total_apps': total_apps,
        'eligible_companies': eligible_companies,
        'selected': selected,
        'rejected': rejected,
        'notes': notes   
    })

# 🔥 RESUME ANALYSIS and upload 


@login_required
def view_resume(request, id):
    student = get_object_or_404(Student, id=id)

    if student.resume:
        return FileResponse(student.resume.open(), content_type='application/pdf')

    return HttpResponse("No resume found")


@login_required
def upload_resume(request):
    student = Student.objects.get(user=request.user)

    if request.method == "POST":
        student.resume = request.FILES.get('resume')
        student.save()

    return redirect('/students/dashboard/')


@login_required
def delete_resume(request):
    student = Student.objects.get(user=request.user)

    if student.resume:
        student.resume.delete()
        student.resume = None
        student.save()

    return redirect('/students/dashboard/')


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

    # EMAIL
    if re.search(r'\S+@\S+\.\S+', content):
        good_points.append("✅ Email present")
    else:
        issues.append("❌ Add email")
        score -= 10

    # PHONE
    if re.search(r'\d{10}', content):
        good_points.append("✅ Phone present")
    else:
        issues.append("❌ Add phone number")
        score -= 10

    # SKILLS
    skills = ["python", "java", "sql", "django", "html", "css", "react"]
    found = [s for s in skills if s in content]

    if len(found) >= 5:
        good_points.append("🔥 Strong skills section")
    elif len(found) >= 2:
        issues.append("⚠ Add more technical skills")
        score -= 10
    else:
        issues.append("❌ No strong skills")
        score -= 20

    # PROJECT
    if "project" in content:
        good_points.append("✅ Projects included")
    else:
        issues.append("⚠ Add project section")
        score -= 10

    # EXPERIENCE
    if "experience" in content or "internship" in content:
        good_points.append("✅ Experience included")
    else:
        issues.append("⚠ Add experience/internship")
        score -= 10

    # LENGTH
    if len(content) < 500:
        issues.append("⚠ Resume too short")
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


# 🔹 APPLY JOB
@login_required
def apply_job(request, job_id):
    from .models import Student, Application
    from companies.models import Job

    student = Student.objects.get(user=request.user)
    job = Job.objects.get(id=job_id)

    # ✅ Prevent duplicate
    if Application.objects.filter(student=student, company=job.company).exists():
        messages.warning(request, "Already applied to this company")
        return redirect('/companies/')

    # ✅ CGPA check
    if student.cgpa < job.min_cgpa:
        messages.error(request, "You are not eligible")
        return redirect('/companies/')

    Application.objects.create(
        student=student,
        company=job.company,
        status="Pending"
    )

    messages.success(request, "Application submitted successfully")
    return redirect('/students/applications/')


# 🔹 ADMIN APPLY JOB
@login_required
def admin_apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    students = Student.objects.all()

    if request.method == "POST":
        student_id = request.POST.get("student_id")
        student = get_object_or_404(Student, id=student_id)

        if Application.objects.filter(student=student, company=job.company).exists():
            return redirect('/companies/')

        if student.cgpa < job.min_cgpa:
            return redirect('/companies/')

        Application.objects.create(
            student=student,
            company=job.company,
            status="Pending"
        )

        return redirect('/companies/')

    return render(request, 'students/admin_apply_job.html', {
        'students': students
    })
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
    notes = Notification.objects.all().order_by('-created_at')

    return render(request, 'students/notifications.html', {
        'notifications': notes   #  FIXED (was notes)
    })


def register_student(request):
    from django.contrib.auth.models import User
    from django.contrib import messages
    from .models import Student

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        name = request.POST.get("name")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, "students/register.html")

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        Student.objects.create(
            user=user,
            name=name,
            email=email,
            cgpa=0
        )

        messages.success(request, "Account created successfully")
        return redirect('/login/')

    return render(request, "students/register.html")

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_notifications(request):

    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            Notification.objects.create(message=message)

    notifications = Notification.objects.all().order_by('-created_at')

    return render(request, "students/admin_notifications.html", {
        "notifications": notifications
    })

@login_required
def delete_notification(request, id):
    notification = get_object_or_404(Notification, id=id)
    notification.delete()
    return redirect('/students/admin-notifications/')

@login_required
def student_notifications(request):
    notes = Notification.objects.all().order_by('-created_at')

    return render(request, "students/notifications.html", {
        "notifications": notes   #  FIXED
    })