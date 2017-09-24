#!/usr/bin/env python

from googlehelper import *
import json

credentials = get_credentials(SCOPE_COURSEWORK)
service = get_service(credentials)
# course_id = '7155852796'  # Computer Programming A1
# course_id = '7621825175'  # Robotics
course_id = '7557587733'  # Computer Programming A4

assignments = []
page_token = None

while True:
    response = service.courses().courseWork(). \
               list(pageToken=page_token, pageSize=100, courseId=course_id). \
               execute()
    assignments.extend(response.get('courseWork', []))
    page_token = response.get('nextPageToken', None)
    if not page_token:
        break

with open('assignments.txt', 'w') as f:
    for assignment in assignments:
        print(assignment['title'],
              ",",
              assignment['id'],
              file=f)

with open('assignments.json', 'w') as f:
    print(json.dumps(response, indent=2), file=f)
