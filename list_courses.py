#!/usr/bin/env python

import googlehelper as gh
import json

credentials = gh.get_credentials(gh.SCOPE_COURSES)
service = gh.get_service(credentials)

courses = gh.download_response_list(service.courses().list,
                                    'courses',
                                    pageSize=100)

with open('courses.txt', 'w') as f:
    for course in courses:
        s = u'{0} {1}\t{2}'.format(
            course['name'], course['section'], course['id'])
        print(s, file=f)

with open('courses.json', 'w') as f:
    print(json.dumps(courses, indent=2), file=f)
