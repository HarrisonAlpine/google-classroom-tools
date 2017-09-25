#!/usr/bin/env python

import googlehelper as gh
import json
import os


if __name__ == '__main__':
    courses = gh.download_courses()
    os.makedirs(gh.DOWNLOAD_DIR)
    txt_file = os.path.join(gh.DOWNLOAD_DIR, 'courses.txt')
    json_file = os.path.join(gh.DOWNLOAD_DIR, 'courses.json')
    with open(txt_file, 'w') as f:
        for course in courses:
            s = u'{0} {1}\t{2}'.format(
                course['name'], course['section'], course['id'])
            print(s, file=f)
    with open(json_file, 'w') as f:
        print(json.dumps(courses, indent=2), file=f)
