from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver


# Create your models here.
class CustomUser(AbstractUser):
    is_student = models.BooleanField(default=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    school = models.CharField(max_length=255, blank=True)
    major = models.CharField(max_length=255, blank=True)
    minor = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    course_watches = models.ManyToManyField('CourseWatch', related_name='students', blank=True)

    def delete(self, *args, **kwargs):
        # Delete associated CourseWatches
        for watch in self.course_watches.all():
            watch.delete()
        super().delete(*args, **kwargs)
    

class SystemState(models.Model):
    is_open = models.BooleanField(default=True)
    
 

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    eagle_id_number = models.CharField(max_length=20)

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.username

class Student(UserProfile):
    school = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    minor = models.CharField(max_length=100, blank=True)
    grad_year = models.IntegerField()
    ## How to see assosciated CourseWatches with a user:
    ### user_profile_instance.course_watches.all()

    def __str__(self):
        return f"{self.user.username} - {self.major}"

class Admin(UserProfile):
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.department}"
    

class Subject(models.Model):
    code = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=255)


    def __str__(self):
        return self.name

class Course(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    credit_option = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.subject.code} - {self.code} {self.name}"
    def students_watching(self):
        return CustomUser.objects.filter(course_watches__section__course=self).distinct()
    
class Section(models.Model):
    course = models.ForeignKey(Course, related_name='sections', on_delete=models.CASCADE)
    number = models.IntegerField(default=0)
    timeslot = models.CharField(max_length=255)  # Adjust the length as needed
    professor = models.CharField(max_length=255)  # Adjust the length as needed
    location = models.CharField(max_length=255)  # Adjust the length as needed
    total_seats = models.IntegerField(default=0)
    used_seats = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.course.name} - Section {self.id}"
    def students_watching(self):
        return CustomUser.objects.filter(course_watches__section=self).distinct()
    

class CourseWatch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    desired_seats = models.IntegerField()
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.section.course.name} - Section {self.section.number}"
    
