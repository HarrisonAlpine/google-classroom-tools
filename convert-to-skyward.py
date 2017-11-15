#!/usr/bin/env python

import googlehelper as gh

course = gh.get_course_from_user()
assignment = gh.get_assignment_from_user(course['id'])
submissions = gh.list_submissions(course['id'], assignment['id'])
grades = [s['assignedGrade'] for s in submissions]

print('\n'.join(str(g) for g in grades))

