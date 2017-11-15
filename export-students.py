#!/usr/bin/env python

import googlehelper as gh

def first_name(student):
   return student['profile']['name']['givenName']

def last_name(student):
   return student['profile']['name']['familyName']

def student_id(student):
   return student['userId']

def get_filename_from_user():
   print('Enter filename')
   return input()

def format_line(student):
   first = first_name(student)
   last = last_name(student)
   _id = student_id(student)
   return '{}\t{}\t{}'.format(_id, first, last)

course = gh.get_course_from_user()
students = gh.list_students(course['id'])
filename = get_filename_from_user()

lines = [format_line(student) for student in students]
output = '\n'.join(lines)
with open(filename, 'w') as f:
   f.write(output)
