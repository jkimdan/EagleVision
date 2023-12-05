from background_task import background
from .models import Subject, Course, Section, Student, CustomUser
import json
import requests
from .utils import send_course_update_email


#change schedule for testing
@background(schedule=20)
def update_course_and_section_data():
    print("test")
    subjects = ['AADS', 'BIOL', 'CHEM', 'COMM', 'CSCI', 'ECON', 'ENGL', 'MATH', 'MFIN', 'NURS', 'POLI']
    for subject_code in subjects:
        response = requests.get(f'http://localhost:8080/waitlist/waitlistcourseofferings?termId=kuali.atp.FA2023-2024&code={subject_code}')
        if response.status_code == 200:
            courses_data = response.json()
            subject_instance, _ = Subject.objects.update_or_create(code=subject_code, defaults={'name': subject_code})

            for course_data in courses_data:
                course_offerings = course_data.get('courseOffering', {})
                if course_offerings:
                    course_code = course_offerings.get('courseOfferingCode', '')
                    course_name = course_offerings.get('name', '')
                    course_description = course_offerings.get('descr', {}).get('formatted', '')
                    credit_option_id = course_offerings.get('creditOptionId', '')
                    credit_option_value = float('.'.join(credit_option_id.split('.')[-2:])) if credit_option_id else None
                    course_instance, _ = Course.objects.update_or_create(subject=subject_instance, code=course_code, defaults={'name': course_name, 'description': course_description, 'credit_option': credit_option_value})

                    course_offering_id = course_offerings.get('id', '')
                    if course_offering_id:
                        activity_response = requests.get(f'http://localhost:8080/waitlist/waitlistactivityofferings?courseOfferingId={course_offering_id}')
                        if activity_response.status_code == 200:
                            sections_data = activity_response.json()

                            for section_data in sections_data:
                                section_details = section_data.get('activityOffering', {})
                                number = int(section_details.get('activityCode', '0'))
                                timeslot = ' '.join(section_data.get('scheduleNames', []))  # Adjust based on actual data structure
                                professor = section_details.get('instructors', [{}])[0].get('personName', 'TBA')
                                location = section_details.get('locationDescription', 'TBA')
                                total_seats = section_details.get('maximumEnrollment', 0)
                                used_seats = section_data.get('activitySeatCount', {}).get('used', 0)
                                
                            
                                Section.objects.update_or_create(
                                    course=course_instance,
                                    number=number,
                                    defaults={
                                        'timeslot': timeslot,
                                        'professor': professor,
                                        'location': location,
                                        'total_seats': total_seats,
                                        'used_seats': used_seats
                                    }
                                )

    print("finish r/w")

    print("starting email loop")
    
    # Loop through all users
    for user in CustomUser.objects.filter(is_student=True):
        # Loop through each user's course watches
        for course_watch in user.course_watches.all():
            section = course_watch.section
            available_seats = section.total_seats - section.used_seats

            # Check if the available seats meet the desired criteria
            if available_seats >= course_watch.desired_seats and not course_watch.sent:
                # Call the email function
                send_course_update_email(user.email, available_seats, section.course, section)
                # Mark the course watch as sent
                course_watch.sent = True
                course_watch.save()

    print("finish email loop")

