from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from .models import CourseWatch, SystemState, CustomUser, Subject, Course, Section
from django.http import HttpResponseRedirect
from .models import CustomUser  # Add this import statement
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import View
import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from .models import Course
from django.contrib.auth import login as auth_login

import os
from django.http import HttpRequest
import requests
from bs4 import BeautifulSoup
from django.db.models import Q

def toggle_system_state(request):
    if request.method == "POST":
        state = SystemState.objects.first()
        state.is_open = not state.is_open
        state.save()
    return redirect('admin_dash')

# FROM AUTH0 WEBSITE 
oauth = OAuth()


oauth.register(
    "auth0", 
    # was "auth0"
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback")),
        connection='google-oauth2'
    )

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    user_info = token['userinfo']

    email = user_info.get('email')

    if email and email.endswith('bc.edu'):
        # Use the email as the username as well
        user, created = CustomUser.objects.get_or_create(username=email, defaults={
            'email': email,
            'first_name': user_info.get('given_name', ''),
            'last_name': user_info.get('family_name', '')
        })
        
        auth_login(request, user)

        if created:
            user.set_unusable_password()
            user.save()
            auth_login(request, user)
            return redirect(reverse('update_profile'))
        else:
            if user.is_student:
                return redirect(reverse('student_search'))
            else: 
                return redirect(reverse('admin_dash'))
    else:
        return render(request, 'LoginPage.html', {'error_message': 'Please use a bc.edu email address.'})


def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

def update_profile(request):
    print(request.user)
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Redirect the user to the dashboard after profile update
            return redirect('student_search')
    else:
        form = CustomUserUpdateForm(instance=request.user)

    return render(request, 'UpdateInfo.html', {'form': form})

def index(request):
    return render(
        request,
        "LoginPage.html",
        context={
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
        },
    )

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('student_search')
    else:
        form = CustomUserCreationForm()
    return render(request, 'RegisterPage.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

def login_with_auth0(request):
    return HttpResponseRedirect(reverse("login"))

# Current implementation does not update API information.
# It adds information to DB upon first access to site and remains constant.
# Could use update_or_create() function, but should a user be able to add/update information to the database (performance concerns with concurrency)? 
def student_search(request):
    all_subjects = Subject.objects.all()
    all_courses = Course.objects.all()
    selected_subjects = request.GET.getlist('subjectCheck')
    selected_credits = request.GET.getlist('credit_filter')
    selected_schools = request.GET.getlist('school_filter')
    search_query = request.GET.get('search_query')

    if not selected_credits:
        selected_credits = ['1', '2', '3', '4']

    if not selected_schools:
        selected_schools = ['MCAS', 'CSOM', 'CSON']

    school_subject_mapping = {
        'MCAS': ['AADS', 'BIOL', 'CHEM', 'COMM', 'CSCI', 'ECON', 'ENGL', 'MATH', 'POLI'],
        'CSOM': ['MFIN'],
        'CSON': ['NURS'],
        'Lynch': [] 
    }

    filtered_courses = Course.objects.all()

    if selected_subjects:
        filtered_courses = filtered_courses.filter(subject__code__in=selected_subjects)

    if selected_schools:
        allowed_subjects = []
        for school in selected_schools:
            allowed_subjects.extend(school_subject_mapping.get(school, []))

        filtered_courses = filtered_courses.filter(subject__code__in=allowed_subjects)


    filtered_courses = filtered_courses.filter(credit_option__in=selected_credits)

    if search_query:
        filtered_courses = filtered_courses.filter(
            Q(name__icontains=search_query) | Q(code__icontains=search_query)
        )

    all_schools = ['MCAS', 'CSOM', 'CSON', 'Lynch']
    paginator = Paginator(filtered_courses, 10)  # Show 25 courses per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "StudentSearch.html", {"page_obj": page_obj, 'subjects': all_subjects, 'courses': filtered_courses, 'facet_subjects': all_subjects, 'all_schools': all_schools})


def student_watchlist(request):
    # return render(request, "StudentWatchlist.html", {'subjects': all_subjects, 'courses': all_courses, 'facet_subjects': all_subjects})
    user = request.user

    user_watchlist = list(user.course_watches.all())
    return render(request, 'StudentWatchlist.html', {'users': user, 'courses': user_watchlist})
# TO DO: 
# Create a view for the add notifactionbutton --> will be different becauseit 
# Will need to process the request and add the course to the watchlsit, thenswitchto watchlsit page 
# @login_required
def admin_dash(request):
    system_state = SystemState.objects.first()
    if not system_state:
        system_state = SystemState.objects.create(is_open=True)
    system_is_open = system_state.is_open
    user = request.user
    return render(request, 'AdminDash.html', {'system_is_open': system_is_open})


@login_required
def add_to_watchlist(request):
    if request.method == 'POST':
        section_id = request.POST.get('section_id')
        desired_seats = request.POST.get('desired_seats')

        # Get the section instance
        section = Section.objects.get(id=section_id)

        # Get the current user
        user = request.user

        # Check if the user already has this section in their watchlist
        if not user.course_watches.filter(section=section).exists():
            # If not, create a new CourseWatch instance
            course_watch = CourseWatch.objects.create(section=section, desired_seats=desired_seats)

            # Add the course_watch to the user's watchlist
            user.course_watches.add(course_watch)

    return redirect('student_watchlist')

def admin_reports(request):
    user = request.user
    if user.is_student:
        messages.warning(request, "Your access is limited to student pages.")
        return redirect('student_search')
    
    
    
    all_subjects = Subject.objects.all()
    all_courses = Course.objects.all()
    selected_subjects = request.GET.getlist('subjectCheck')
    selected_credits = request.GET.getlist('credit_filter')
    selected_schools = request.GET.getlist('school_filter')
    search_query = request.GET.get('search_query')

    if not selected_credits:
        selected_credits = ['1', '2', '3', '4']

    if not selected_schools:
        selected_schools = ['MCAS', 'CSOM', 'CSON']

    school_subject_mapping = {
        'MCAS': ['AADS', 'BIOL', 'CHEM', 'COMM', 'CSCI', 'ECON', 'ENGL', 'MATH', 'POLI'],
        'CSOM': ['MFIN'],
        'CSON': ['NURS'],
        'Lynch': [] 
    }

    filtered_courses = Course.objects.all()

    if selected_subjects:
        filtered_courses = filtered_courses.filter(subject__code__in=selected_subjects)

    if selected_schools:
        allowed_subjects = []
        for school in selected_schools:
            allowed_subjects.extend(school_subject_mapping.get(school, []))

        filtered_courses = filtered_courses.filter(subject__code__in=allowed_subjects)


    filtered_courses = filtered_courses.filter(credit_option__in=selected_credits)

    if search_query:
        filtered_courses = filtered_courses.filter(
            Q(name__icontains=search_query) | Q(code__icontains=search_query)
        )

    all_schools = ['MCAS', 'CSOM', 'CSON', 'Lynch']
    paginator = Paginator(filtered_courses, 10)  # Show 25 courses per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "AdminReports.html", {"page_obj": page_obj, 'subjects': all_subjects, 'courses': filtered_courses, 'facet_subjects': all_subjects, 'all_schools': all_schools})


def course_report(request, course_id):
    course = get_object_or_404(Course, code=course_id)
    most_watched_section = course.sections.annotate(watch_count=Count('coursewatch')).order_by('-watch_count').first()
    context = {
        'course': course,
        'most_watched_section': most_watched_section,
    }
    return render(request, 'CourseReport.html', context)


def remove_course(request, course_code):
    user = request.user
    course_watch = get_object_or_404(CourseWatch, user=user, section__course__code=course_code)
    course_watch.delete()
    return redirect('student_watchlist')

def generate_watchlist_pdf(request, course_id):
    # Get the course object
    course = get_object_or_404(Course, code=course_id)

    # Create a response object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{course.code}_watchlist.pdf"'

    # Create a PDF document
    p = canvas.Canvas(response, pagesize=letter)

    # Add the course code at the top of the page
   
    p.setFont("Helvetica-Bold", 16) 
    p.drawCentredString(letter[0] / 2, letter[1] - 50, f"{course.code} Watchlist")
    p.setFont("Helvetica", 12) 
    p.drawCentredString(letter[0] / 2, letter[1] - 80, f"Generated on {datetime.now()}")

    # Create a list to store the data for the table
    data = [['ID', 'Student Name', 'YOG', 'Email', 'School', 'Major', 'Sections', 'Desired Seats']]

    # Add watchlist data to the list
    for i, student in enumerate(course.students_watching()):
        sections = ", ".join([f"Section {course_watch.section.number}" for course_watch in student.course_watches.filter(section__course=course)])
        data.append([i + 1, f"{student.first_name} {student.last_name}", student.graduation_year, student.email, student.school, student.major, sections, student.course_watches.first().desired_seats])

    # Create a Table object with the watchlist data
    watchlist_table = Table(data)

    # Apply styles to the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ])
    watchlist_table.setStyle(style)

    # Draw the table on the PDF
    watchlist_table.wrapOn(p, 0, 0)
    watchlist_table.drawOn(p, 50, 600)

    # Save the PDF document
    p.showPage()
    p.save()

    return response
