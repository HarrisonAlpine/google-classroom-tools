#!/usr/bin/env python

import googlehelper as gh
import json
import os


def assignment_submission_string(assignment_submission):
    student_id = assignment_submission['userId']
    student = student_id_dict[student_id]
    student_name = student['profile']['name']['fullName']
    assignment_state = assignment_submission['state']
    assignment_id = assignment_submission['id']
    try:
        attachments = assignment_submission['assignmentSubmission']\
                                           ['attachments']
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
    assignment = gh.get_assignment_from_user(course_id)
    course_work_id = assignment['id']
    assignment_submissions = gh.list_submissions(course_id, course_work_id)
    gh.download_assignment_submissions(course_id, course_work_id, 
                                       assignment_submissions=assignment_submissions,
                                       course=course, course_work=assignment)
    
    course_work_dir = gh.get_course_work_dir(assignment, course=course)
    os.makedirs(course_work_dir, exist_ok=True)
    student_id_dict = gh.create_student_id_dict(course_id)

    txt_file = os.path.join(course_work_dir, 'submissions.txt')
    json_file = os.path.join(course_work_dir, 'submissions.json')
    with open(txt_file, 'w') as f:
        for assignment_submission in assignment_submissions:
            line = assignment_submission_string(assignment_submission)
            print(line, file=f)
    with open(json_file, 'w') as f:
        print(json.dumps(assignment_submissions, indent=2), file=f)
    # with open(txt_file) as f:
    #     print(f.read())
