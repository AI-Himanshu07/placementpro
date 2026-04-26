from django.shortcuts import render, redirect, get_object_or_404
from .models import Company, Job
from django.contrib.auth.decorators import login_required, user_passes_test
import openpyxl
from django.http import HttpResponse
from students.models import Student, Application
from django.contrib.auth.decorators import login_required


def is_staff(user):
    return user.is_staff


def company_list(request):
    from companies.models import Company

    companies = Company.objects.all()

    return render(request, 'companies/company_list.html', {'companies': companies})

@login_required
def company_detail(request, id):
    company = get_object_or_404(Company, id=id)

    student = Student.objects.filter(user=request.user).first()

    jobs = Job.objects.filter(company=company)

    return render(request, 'companies/company_detail.html', {
        'company': company,
        'jobs': jobs,
        'student': student
    })


@login_required
@user_passes_test(is_staff)
def add_company(request):
    if request.method == 'POST':
        Company.objects.create(
            name=request.POST.get('name'),
            role=request.POST.get('role'),
            min_cgpa=request.POST.get('min_cgpa'),
            job=request.POST.get('job'),
        )
        return redirect('/companies/')
    return render(request, 'companies/add_company.html')


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


@login_required
@user_passes_test(is_staff)
def delete_company(request, id):
    company = get_object_or_404(Company, id=id)
    company.delete()
    return redirect('/companies/')

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

@login_required
def update_status(request, app_id, status):
    app = get_object_or_404(Application, id=app_id)

    company = Company.objects.filter(user=request.user).first()

    # 🔒 सुरक्षा check (very important)
    if not company or app.company != company:
        return redirect('/')

    if status in ['Selected', 'Rejected']:
        app.status = status
        app.save()

    return redirect('/companies/applications/')

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

@login_required
def company_applications(request):
    company = Company.objects.filter(user=request.user).first()

    if not company:
        return redirect('/')

    applications = Application.objects.filter(company=company)

    return render(request, 'companies/applications.html', {
        'applications': applications
    })

@login_required
def company_jobs(request):
    company = Company.objects.filter(user=request.user).first()

    if not company:
        return redirect('/')

    jobs = Job.objects.filter(company=company)

    return render(request, 'companies/jobs.html', {
        'jobs': jobs
    })

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
@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    company = Company.objects.filter(user=request.user).first()

    if job.company == company:
        job.delete()

    return redirect('/companies/jobs/')

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