from django.contrib import admin
from .models import *

# Register your models here.

class SectionInline(admin.TabularInline):
    model = Section
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    inlines = [SectionInline]

class CourseInline(admin.TabularInline):
    model = Course
    extra = 0

class SubjectAdmin(admin.ModelAdmin):
    inlines = [CourseInline]

class CourseWatchInline(admin.TabularInline):
    model = CustomUser.course_watches.through
    extra = 0
    fields = ('coursewatch', 'display_desired_seats')
    readonly_fields = ('display_desired_seats',)

    def display_desired_seats(self, instance):
        # This method retrieves the desired_seats for the CourseWatch
        return instance.coursewatch.desired_seats
    display_desired_seats.short_description = 'Desired Seats'

class CustomUserAdmin(admin.ModelAdmin):
    inlines = [CourseWatchInline]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Subject, SubjectAdmin)

# Register CourseWatch for direct access in admin
class CourseWatchAdmin(admin.ModelAdmin):
    list_display = ('section', 'desired_seats', 'list_users')

    def list_users(self, obj):
        return ", ".join([user.username for user in obj.students.all()])
    list_users.short_description = 'Users'

admin.site.register(CourseWatch, CourseWatchAdmin)