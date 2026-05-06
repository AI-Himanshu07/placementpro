from django.shortcuts import render, redirect, get_object_or_404
from .models import Company, Job
from django.contrib.auth.decorators import login_required, user_passes_test
import openpyxl
from django.http import HttpResponse
from students.models import Student, Application


def is_staff(user):
    return user.is_staff


# 🔹 COMPANY LIST
def company_list(request):
    query = request.GET.get('q')

    companies = Company.objects.all()

    if query:
        companies = companies.filter(name__icontains=query)

    applied_companies = []
    student = None

    if request.user.is_authenticated:
        try:
            student = Student.objects.get(user=request.user)

            applied_companies = Application.objects.filter(
                student=student
            ).values_list('company_id', flat=True)

        except Student.DoesNotExist:
            pass

    return render(request, 'companies/company_list.html', {
        'companies': companies,
        'student': student,
        'applied_companies': applied_companies
    })


# 🔹 COMPANY DETAIL
@login_required
def company_detail(request, id):
    company = get_object_or_404(Company, id=id)

    student = Student.objects.filter(user=request.user).first()

    # 🔥 IMPORTANT FIX: load jobs of this company
    jobs = Job.objects.filter(company=company)

    return render(request, 'companies/company_detail.html', {
        'company': company,
        'jobs': jobs,   # ✅ REQUIRED
        'student': student
    })


# 🔹 ADD COMPANY
@login_required
@user_passes_test(is_staff)
def add_company(request):
    if request.method == 'POST':
        Company.objects.create(
            name=request.POST.get('name'),
            role=request.POST.get('role'),
            min_cgpa=request.POST.get('min_cgpa'),
            job=request.POST.get('job'),  # old field (kept same)
        )
        return redirect('/companies/')
    return render(request, 'companies/add_company.html')


# 🔹 EDIT COMPANY
@login_required
@user_passes_test(is_staff)
def edit_company(request, id):
    company = get_object_or_404(Company, id=id)

    if request.method == 'POST':
        company.name = request.POST.get('name')
        company.role = request.POST.get('role')
        company.min_cgpa = request.POST.get('min_cgpa')
        company.job = request.POST.get('job')
        company.save()
        return redirect('/companies/')

    return render(request, 'companies/edit_company.html', {'company': company})


# 🔹 DELETE COMPANY
@login_required
@user_passes_test(is_staff)
def delete_company(request, id):
    company = get_object_or_404(Company, id=id)
    company.delete()
    return redirect('/companies/')


# 🔹 COMPANY DASHBOARD
@login_required
def company_dashboard(request):
    company = Company.objects.filter(user=request.user).first()

    if not company:
        return redirect('/')

    applications = Application.objects.filter(company=company)

    selected = applications.filter(status='Selected').count()
    rejected = applications.filter(status='Rejected').count()

    return render(request, 'companies/company_dashboard.html', {
        'company': company,
        'applications': applications,
        'total_apps': applications.count(),
        'selected': selected,
        'rejected': rejected
    })


# 🔹 UPDATE STATUS
@login_required
def update_status(request, app_id, status):
    app = get_object_or_404(Application, id=app_id)

    company = Company.objects.filter(user=request.user).first()

    if not company or app.company != company:
        return redirect('/')

    if status in ['Selected', 'Rejected']:
        app.status = status
        app.save()

    return redirect('/companies/applications/')


# 🔹 DOWNLOAD COMPANIES
@login_required
def download_companies(request):
    wb = openpyxl.Workbook()
    ws = wb.active

    ws.append(['Name', 'Role', 'Min CGPA'])

    for company in Company.objects.all():
        ws.append([company.name, company.role, company.min_cgpa])

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=companies.xlsx'
    wb.save(response)

    return response


# 🔹 COMPANY APPLICATIONS
@login_required
def company_applications(request):
    company = Company.objects.filter(user=request.user).first()

    if not company:
        return redirect('/')

    applications = Application.objects.filter(company=company)

    return render(request, 'companies/applications.html', {
        'applications': applications
    })


# 🔹 COMPANY JOBS
@login_required
def company_jobs(request):
    company = Company.objects.filter(user=request.user).first()

    if not company:
        return redirect('/')

    jobs = Job.objects.filter(company=company)

    # 🔥 FIX: add student (for eligibility UI)
    student = Student.objects.filter(user=request.user).first()

    return render(request, 'companies/jobs.html', {
        'jobs': jobs,
        'student': student   # ✅ IMPORTANT
    })


# 🔹 ADD JOB
@login_required
def add_job(request):
    company = Company.objects.filter(user=request.user).first()

    if not company:
        return redirect('/')

    if request.method == "POST":
        Job.objects.create(
            company=company,
            title=request.POST.get('title'),
            job_type=request.POST.get('job_type'),
            description=request.POST.get('description'),
            min_cgpa=request.POST.get('min_cgpa')
        )
        return redirect('/companies/jobs/')

    return render(request, 'companies/add_job.html')


# 🔹 DELETE JOB
@login_required
def delete_job(request, id):
    job = get_object_or_404(Job, id=id)

    company = Company.objects.filter(user=request.user).first()

    if job.company == company:
        job.delete()

    return redirect('/companies/jobs/')


# 🔹 EDIT JOB
@login_required
def edit_job(request, id):
    job = get_object_or_404(Job, id=id)

    if request.method == "POST":
        job.title = request.POST.get('title')
        job.description = request.POST.get('description')
        job.min_cgpa = request.POST.get('min_cgpa')
        job.job_type = request.POST.get('job_type')
        job.save()
        return redirect('/companies/jobs/')

    return render(request, 'companies/edit_job.html', {'job': job})


# 🔹 VIEW JOB 
@login_required
def view_job(request, id):
     print("VIEW JOB HIT", id)  

     job = get_object_or_404(Job, id=id)

     return render(request, 'companies/view_job.html', {
        'job': job
    })