#!/usr/bin/env python

import googlehelper as gh
import json
import os

credentials = gh.get_credentials(gh.SCOPE_COURSEWORK)
service = gh.get_service(credentials)
drive_credentials = gh.get_credentials(gh.SCOPE_DRIVE)
drive_service = gh.get_drive_service(drive_credentials)
# course_id = '7155852796'  # Computer Programming A1
# course_id = '7621825175'  # Robotics
course_id = '7557587733'  # Computer Programming A4

course_work_id = '7672332153'  # Lab 3

student_dict = {}

with open('students.json') as f:
    students = json.load(f)

for student in students:
    student_dict[student['userId']] = student['profile']['name']['fullName']

fn = service.courses().courseWork().studentSubmissions().list
submissions = gh.download_response_list(fn,
                                        'studentSubmissions',
                                        courseId=course_id,
                                        courseWorkId=course_work_id,
                                        pageSize=100)

download_dir = 'downloads'
if not os.path.exists(download_dir):
    os.makedirs(download_dir)


with open('submissions.txt', 'w') as f:
    for submission in submissions:
        try:
            attachment = submission['assignmentSubmission']['attachments'][0]
            file_id = attachment['driveFile']['id']
            user_id = submission['userId']
            username = student_dict.get(user_id, 'unknown')
            filename = '{}{}{}.{}'.format(
                download_dir,
                os.path.sep,
                username,
                'zip')
            gh.download_file(drive_service, file_id, filename)
            results = drive_service.files().get_media(fileId=file_id).execute()
        except KeyError:
            file_id = 'No file submitted'
        print(submission['userId'],
              "\t",
              file_id,
              file=f)

with open('submissions.json', 'w') as f:
    print(json.dumps(submissions, indent=2), file=f)
