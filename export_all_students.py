#!/usr/bin/env python

import googlehelper as gh
from export_students import export_students

def period_from_course(course):
   s = course['section']
   if not s:
      s = course['name']
   first, _, _ = s.partition(' ')
   return first

courses = gh.list_courses()
for course in courses:
   students = gh.list_students(course['id'])
   period = period_from_course(course)
   filename = '{}-google-students.csv'.format(period)
   export_students(students, filename)
