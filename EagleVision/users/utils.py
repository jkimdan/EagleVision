from django.core.mail import send_mail
from django.conf import settings
from .models import Course, Section

def send_course_update_email(email, seats, course: Course, section: Section):
    subject = f'Update on {course.name}'
    message = f'Hello,\n\nThere are now {seats} seats available in the course:\n\n{course.name}\n{section.professor}\n{section.timeslot}\n\nBest,\nEagleVision Notification System'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    send_mail(subject, message, email_from, recipient_list)