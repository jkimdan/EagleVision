from django.apps import AppConfig

class YourAppConfig(AppConfig):
    name = 'users'

    def ready(self):
        from .tasks import update_course_and_section_data
        update_course_and_section_data(repeat=20)
