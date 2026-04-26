from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
email = "admin@gmail.com"
password = "admin123"

user, created = User.objects.get_or_create(username=username)

user.email = email
user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.save()