#!/usr/bin/env python

from googlehelper import *
import json
import os


credentials = get_credentials(SCOPE_COURSEWORK)
service = get_service(credentials)
drive_credentials = get_credentials(SCOPE_DRIVE)
drive_service = get_drive_service(drive_credentials)
# course_id = '7155852796'  # Computer Programming A1
# course_id = '7621825175'  # Robotics
course_id = '7557587733'  # Computer Programming A4

course_work_id = '7672332153'  # Lab 3

student_dict = {}

with open('students.txt') as f:
    data = f.read().strip()
    ls = data.split('\n')
    for l in ls:
        n, i = [s.strip() for s in l.split(',')]
        student_dict[i] = n

submissions = []
page_token = None

while True:
    response = service.courses().courseWork().studentSubmissions(). \
               list(pageToken=page_token, pageSize=100, courseId=course_id,
                    courseWorkId=course_work_id). \
               execute()
    submissions.extend(response.get('studentSubmissions', []))
    page_token = response.get('nextPageToken', None)
    if not page_token:
        break


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
            download_file(drive_service, file_id, filename)
            results = drive_service.files().get_media(fileId=file_id).execute()
        except KeyError:
            file_id = 'No file submitted'
        print(submission['userId'],
              ",",
              file_id,
              file=f)

with open('submissions.json', 'w') as f:
    print(json.dumps(response, indent=2), file=f)
