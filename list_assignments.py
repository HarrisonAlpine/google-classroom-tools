#!/usr/bin/env python

import googlehelper as gh
import json
import os

# DEFAULT_COURSE_ID = '7155852796'  # Computer Programming A1
# DEFAULT_COURSE_ID = '7621825175'  # Robotics
DEFAULT_COURSE_ID = '7557587733'  # Computer Programming A4


if __name__ == '__main__':
    # course = gh.download_course(DEFAULT_COURSE_ID)
    # assignments = gh.download_assignments(DEFAULT_COURSE_ID)
    course = gh.get_course_from_user()
    course_id = course['id']
    assignments = gh.download_assignments(course_id)

    course_dir = gh.get_course_dir(course)
    os.makedirs(course_dir, exist_ok=True)

    txt_file = os.path.join(course_dir, 'assignments.txt')
    json_file = os.path.join(course_dir, 'assignments.json')
    with open(txt_file, 'w') as f:
        for assignment in assignments:
            line = '{}\t{}'.format(assignment['title'],
                                   assignment['id'])
            print(line, file=f)
    with open(json_file, 'w') as f:
        print(json.dumps(assignments, indent=2), file=f)
