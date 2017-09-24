#!/usr/bin/env python

import googlehelper as gh
import json

credentials = gh.get_credentials(gh.SCOPE_COURSEWORK)
service = gh.get_service(credentials)
# course_id = '7155852796'  # Computer Programming A1
# course_id = '7621825175'  # Robotics
course_id = '7557587733'  # Computer Programming A4

assignments = gh.download_response_list(service.courses().courseWork().list,
                                        'courseWork', courseId=course_id,
                                        pageSize=100)

with open('assignments.txt', 'w') as f:
    for assignment in assignments:
        print(assignment['title'],
              "\t",
              assignment['id'],
              file=f)

with open('assignments.json', 'w') as f:
    print(json.dumps(assignments, indent=2), file=f)
