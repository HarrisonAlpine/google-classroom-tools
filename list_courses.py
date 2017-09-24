#!/usr/bin/env python

from googlehelper import *

credentials = get_credentials(SCOPE_COURSES)
service = get_service(credentials)
results = service.courses().list(pageSize=10).execute()
courses = results.get('courses', [])
filename = 'courses.txt'

with open(filename, 'w') as f:
    for course in courses:
        s = u'{0} {1}, {2}'.format(
            course['name'], course['section'], course['id'])
        print(s, file=f)
