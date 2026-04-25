from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    min_cgpa = models.FloatField()
    job = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=100)
    job_type = models.CharField(max_length=50)
    description = models.TextField()
    min_cgpa = models.FloatField()
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"{self.company.name} - {self.title}"


class CompanyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)

    def __str__(self):
        return self.company_name