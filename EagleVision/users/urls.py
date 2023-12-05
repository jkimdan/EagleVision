from django.urls import path
from . import views
from .views import register_view, student_search, admin_dash, toggle_system_state, logout_view, add_to_watchlist, admin_reports, course_report, remove_course, generate_watchlist_pdf
from . import views

urlpatterns = [
    # path('login/', login_view, name='login_view'),
    path('register/', register_view, name='register_view'),
    path('student_search/', student_search, name='student_search'),
    path('admin_dash/', admin_dash, name='admin_dash'),
    path('admin_reports/', admin_reports, name='admin_reports'),
    path('toggle_system_state/', toggle_system_state, name='toggle_system_state'),
    path('logout/', logout_view, name='logout_view'),
    path('add_to_watchlist/', add_to_watchlist, name='add_to_watchlist'),
    path('course_report/<str:course_id>/', course_report, name='course_report'),
    # path('generate_pdf_report/<course_id>/', CourseReportPDFView.as_view(), name='generate_pdf_report'),

# Index is the main page -- it is the login page , which also has logic to go
# right to the other pages if already logged in (check this is correct)
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path("login_with_auth0", views.login_with_auth0, name="login_with_auth0"),
    path("student_watchlist", views.student_watchlist, name="student_watchlist"),
    path('update', views.update_profile, name='update_profile'),
    path('remove_course/<str:course_code>/', remove_course, name='remove_course'),
    path('course/<str:course_id>/watchlist/pdf/', generate_watchlist_pdf, name='generate_watchlist_pdf'),

]