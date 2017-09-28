#!/usr/bin/env python

import googlehelper as gh
import json
import os


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
    assignment = gh.get_assignment_from_user(course_id)
    course_work_id = assignment['id']
    submissions = gh.list_submissions(course_id, course_work_id)
    assignment_dir = gh.get_course_work_dir(assignment, course=course,
                                            timeStamp=True)

    gh.download_assignment_submissions(course_id, course_work_id,
                                       submissions=submissions,
                                       course=course, course_work=assignment,
                                       assignment_dir=assignment_dir)

    os.makedirs(assignment_dir, exist_ok=True)
    student_id_dict = gh.create_student_id_dict(course_id)

    txt_file = os.path.join(assignment_dir, 'submissions.txt')
    json_file = os.path.join(assignment_dir, 'submissions.json')
    with open(txt_file, 'w') as f:
        for submission in submissions:
            line = submission_string(submission)
            print(line, file=f)
    with open(json_file, 'w') as f:
        print(json.dumps(submissions, indent=2), file=f)
    # with open(txt_file) as f:
    #     print(f.read())
