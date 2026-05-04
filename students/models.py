from django.db import models
from django.contrib.auth.models import User
from companies.models import Company
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver

from django.db.models.signals import pre_save


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    cgpa = models.FloatField()
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)

    def __str__(self):
        return self.name

class Application(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='applications')

    status = models.CharField(max_length=20, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'company')  

    def __str__(self):
        return f"{self.student.name} -> {self.company.name}"

class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
    
@receiver(post_delete, sender=Student)
def delete_resume_file(sender, instance, **kwargs):
    if instance.resume:
        if os.path.isfile(instance.resume.path):
            os.remove(instance.resume.path)    
    
@receiver(pre_save, sender=Student)
def delete_old_resume(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old = Student.objects.get(pk=instance.pk)
    except Student.DoesNotExist:
        return

    old_file = old.resume
    new_file = instance.resume

    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)    