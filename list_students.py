#!/usr/bin/env python

# from googlehelper import *
import googlehelper as gh
import json

credentials = gh.get_credentials(gh.SCOPE_ROSTERS)
service = gh.get_service(credentials)
# course_id = '7155852796'  # Computer Programming A1
# course_id = '7621825175'  # Robotics
course_id = '7557587733'  # Computer Programming A4

# students = []
# page_token = None


# while True:
#     response = service.courses().students(). \
#                list(pageToken=page_token, pageSize=100, courseId=course_id). \
#                execute()
#     students.extend(response.get('students', []))
#     page_token = response.get('nextPageToken', None)
#     if not page_token:
#         break
students = gh.download_response_list(service.courses().students().list,
                                     'students', courseId=course_id,
                                     pageSize=100)

with open('students.txt', 'w') as f:
    for student in students:
        print(student['profile']['name']['fullName'],
              "\t",
              student['profile']['id'],
              file=f)

with open('students.json', 'w') as f:
    print(json.dumps(students, indent=2), file=f)
