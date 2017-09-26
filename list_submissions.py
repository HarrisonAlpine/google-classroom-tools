#!/usr/bin/env python

import googlehelper as gh
# from googlehelper import *
import json
import os


# credentials = get_credentials([SCOPE_COURSES, SCOPE_COURSEWORK])
# service = get_service(credentials)
# drive_credentials = get_credentials(SCOPE_DRIVE)
# drive_service = get_drive_service(drive_credentials)
course_id = '7155852796'  # Computer Programming A1
# course_id = '7621825175'  # Robotics
# course_id = '7557587733'  # Computer Programming A4

# Computer Programming A1
# course_work_id = '7155748386'  # Lab1
# course_work_id = '7560508750'  # Lab 2
course_work_id = '7665087531'  # Lab 3
# course_work_id = '7776161915'  # Lab 4

# Computer Programming A4
# course_work_id = '7572239038'  # Lab 1
# course_work_id = '7567561168'  # Lab 2
# course_work_id = '7672332153'  # Lab 3
# course_work_id = '7775810957'  # Lab 4

# course = service.courses().get(id=course_id).execute()
# course_name = course['name'] + ' ' + course['section']
course = gh.download_course(course_id)

# course_work = service.courses().courseWork().get(courseId=course_id, id=course_work_id).execute()
# course_work_title = course_work['title']
course_work = gh.download_course_work(course_id, course_work_id)

student_dict = {}
student_id_dict = {}

# with open('students.txt') as f:
    # data = f.read().strip()
    # ls = data.split('\n')
    # for l in ls:
        # n, i = [s.strip() for s in l.split(',')]
        # student_dict[i] = n
students = gh.download_students(course_id)
for student in students:
    student_dict[student['userId']] = student['profile']['name']['fullName']
    student_id_dict[student['userId']] = student

# submissions = []
# page_token = None

# while True:
    # response = service.courses().courseWork().studentSubmissions(). \
               # list(pageToken=page_token, pageSize=100, courseId=course_id,
                    # courseWorkId=course_work_id). \
               # execute()
    # submissions.extend(response.get('studentSubmissions', []))
    # page_token = response.get('nextPageToken', None)
    # if not page_token:
        # break
submissions = gh.download_submissions(course_id, submission_id)

# def format_filename(s):
    # """Take a string and return a valid filename constructed from the string.
# Uses a whitelist approach: any characters not present in valid_chars are
# removed. Also spaces are replaced with underscores.
 
# Note: this method may produce invalid filenames such as ``, `.` or `..`
# When I use this method I prepend a date string like '2009_01_15_19_46_32_'
# and append a file extension like '.txt', so I avoid the potential of using
# an invalid filename.

# Stolen from https://gist.github.com/seanh/93666
 
# """
    # import string
    # valid_chars = "-_.() %s%s%s" % (string.ascii_letters, string.digits, os.path.sep)
    # filename = ''.join(c for c in s if c in valid_chars)
    # return filename
 
# download_dir = os.path.join('downloads', course_name, course_work_title)
# download_dir = format_filename(download_dir)
# if not os.path.exists(download_dir):
    # os.makedirs(download_dir)

course_work_dir = gh.get_course_work_dir(course_work, course)
os.makedirs(course_work_dir, exist_ok=True)

# def get_download_filename(assignment_dir, student_name, submission_filename):
    # return os.path.join(assignment_dir, student_name + '--' + submission_filename)

with open('submissions.json', 'w') as f:
    print(json.dumps(submissions, indent=2), file=f)

for submission in submissions:
    # Sometimes people don't mark it as submitted
    # if submission['state'] != TURNED_IN:
        # continue
    try:
        # attachment = submission['assignmentSubmission']['attachments'][0]
        user_id = submission['userId']
        # print('user_id', user_id)
        student_name = student_dict.get(user_id, 'unknown')
        print(student_name)
        for attachment in submission['assignmentSubmission']['attachments']:
            file_id = attachment['driveFile']['id']
            file_name = attachment['driveFile']['title']
            print('\tSubmitted:', file_name)
            download_filename = get_download_filename(download_dir, student_name, file_name)
            # filename = '{}{}{}.{}'.format(
                # download_dir,
                # os.path.sep,
                # student_name,
                # 'zip')
            download_file(drive_service, file_id, download_filename)
            # results = drive_service.files().get_media(fileId=file_id).execute()
    except KeyError:
        file_id = 'No file submitted'
        
with open('submissions.txt', 'w') as f:
    for submission in submissions:
        print(submission['userId'],
              ',',
              file_id,
              file=f)

