#!/usr/bin/env python

import googlehelper as gh

def first_name(student):
   return student['profile']['name']['givenName']

def last_name(student):
   return student['profile']['name']['familyName']

def student_id(student):
   return student['userId']

def email(student):
   return student['profile']['emailAddress']

def get_filename_from_user():
   print('Enter filename')
   return input()

def format_line(student):
   first = first_name(student)
   last = last_name(student)
   _email = email(student)
   _id = student_id(student)
   return '{}\t{}\t{}\t{}'.format(_id, first, last, _email)

def format_students(students):
   lines = [format_line(student) for student in students]
   return '\n'.join(lines)

def export_students(students, filename):
   with open(filename, 'w') as f:
      f.write(format_students(students))

if __name__ == '__main__':
   course = gh.get_course_from_user()
   students = gh.list_students(course['id'])
   filename = get_filename_from_user()
   export_students(students, filename)
   
