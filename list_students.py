#!/usr/bin/env python

import googlehelper as gh
import json
import os

# DEFAULT_COURSE_ID = '7155852796'  # Computer Programming A1
# DEFAULT_COURSE_ID = '7621825175'  # Robotics
DEFAULT_COURSE_ID = '7557587733'  # Computer Programming A4

if __name__ == '__main__':
    course = gh.download_course(DEFAULT_COURSE_ID)
    students = gh.download_students(DEFAULT_COURSE_ID)

    course_name = gh.course_full_name(course)
    course_dir_name = gh.make_string_safe_filename(course_name)
    course_dir = os.path.join(gh.DOWNLOAD_DIR, course_dir_name)
    os.makedirs(course_dir)

    txt_file = os.path.join(course_dir, 'students.txt')
    json_file = os.path.join(course_dir, 'students.json')
    with open(txt_file, 'w') as f:
        for student in students:
            line = '{}\t{}'.format(student['profile']['name']['fullName'],
                                   student['profile']['id'])
            print(line, file=f)
    with open(json_file, 'w') as f:
        print(json.dumps(students, indent=2), file=f)
