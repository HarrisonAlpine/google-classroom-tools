# for interactive
import googlehelper as gh
import json
import os

ROOT_DIR = os.path.join(os.path.expanduser('~'), 'class-downloads')

course = gh.get_course_from_user()
course_id = course['id']
assignment = gh.get_assignment_from_user(course_id)
course_work_id = assignment['id']
submissions = gh.list_submissions(course_id, course_work_id)
assignment_dir = gh.get_course_work_dir(assignment, course=course,
                                        timeStamp=True,
                                        root_dir=ROOT_DIR)
assignment_dir += '--UNRETURNED'

from googlehelper import *

course_work = get_course_work(course_id, course_work_id)
drive_service = get_drive_service_from_scope(SCOPE_DRIVE)
student_id_dict = create_student_id_dict(course_id)
os.makedirs(assignment_dir, exist_ok=True)
new_submissions = [s for s in submissions if s['state'] != 'RETURNED']

def download_submissions(submissions):
    for submission in submissions:
        user_id = submission['userId']
        student_name = student_id_dict[user_id]['profile']['name']['fullName']
        try:
            download_assignment_submission_files(submission, student_name,
                                                assignment_dir, drive_service)
        except:
            print('Could not download {}\'s file'.format(student_name))

print('''
New submissions are stored in new_submissions. Once you have filtered the new
submissions to your liking, pass them into the download_submissions function.
''')
