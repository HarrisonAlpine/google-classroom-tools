#!/usr/bin/env python

import googlehelper as gh
import json
import os

ROOT_DIR = os.path.join(os.path.expanduser('~'), 'class-downloads')

def submission_string(submission):
    student_id = submission['userId']
    student = student_id_dict[student_id]
    student_name = student['profile']['name']['fullName']
    assignment_state = submission['state']
    assignment_id = submission['id']
    try:
        attachments = submission['assignmentSubmission']['attachments']
        attachment_names = ' '.join([a['driveFile']['title'] for a in
                                     attachments])
    except KeyError:
        attachment_names = 'N/A'
    return '\t'.join([student_name,
                      attachment_names,
                      assignment_state,
                      assignment_id])


if __name__ == '__main__':
    course = gh.get_course_from_user()
    course_id = course['id']
    assignments = gh.list_assignments(course_id)
    assignment_submissions = {}
    for assignment in assignments:
        assignment_dir = gh.get_course_work_dir(assignment, course=course,
                                                timeStamp=False,
                                                root_dir=ROOT_DIR)
        gh.download_done_assignment_submissions(course_id, assignment['id'], 
                                                course=course, course_work=assignment,
                                                assignment_dir=assignment_dir)
