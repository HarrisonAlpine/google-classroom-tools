import httplib2
import os

import io
from apiclient.http import MediaIoBaseDownload
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/classroom.googleapis.com-python-quickstart.json
# SCOPES = 'https://www.googleapis.com/auth/classroom.courses.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Mr. McCullough Custom Tools'

SCOPE_PREFIX = 'https://www.googleapis.com/auth/'

SCOPE_COURSES = SCOPE_PREFIX + 'classroom.courses.readonly'
SCOPE_COURSEWORK = SCOPE_PREFIX + 'classroom.coursework.students.readonly'
SCOPE_ROSTERS = SCOPE_PREFIX + 'classroom.rosters.readonly'
SCOPE_STUDENT_SUBMISSIONS = SCOPE_PREFIX + \
                            'classroom.student-submissions.students.readonly'
SCOPE_DRIVE = SCOPE_PREFIX + 'drive.readonly'

SCOPE_ALL = [SCOPE_COURSES,
             SCOPE_COURSEWORK,
             SCOPE_ROSTERS,
             SCOPE_STUDENT_SUBMISSIONS,
             SCOPE_DRIVE]

CREDENTIALS_SUFFIX = '-credentials.json'


def safe_name_from_scope(scope):
    return scope.rsplit('/', 1)[-1]


def credentials_file_from_scope(scope):
    return safe_name_from_scope(scope) + CREDENTIALS_SUFFIX


def credentials_file_from_scopes(scopes):
    return '-'.join([safe_name_from_scope(s) for s in scopes]) + \
        CREDENTIALS_SUFFIX


DOWNLOAD_DIR = 'downloads'
JSON_DIR = 'json'
TXT_DIR = 'txt'

ASSIGNMENT = 'ASSIGNMENT'


def get_credentials(scope):
    if type(scope) is str:
        credential_name = credentials_file_from_scope(scope)
        # if scope not in CREDENTIAL_FROM_SCOPE:
        #     raise Exception('Scope (' + scope + ') is invalid.')
        # credential_name = CREDENTIAL_FROM_SCOPE[scope]
    else:
        credential_name = credentials_file_from_scope('-'.join(scope))
        # for s in scope:
        #     if s not in CREDENTIAL_FROM_SCOPE:
        #         raise Exception('Scope "' + s + '" was invalid.')
        # credential_name = CREDENTIAL_MULTIPLE
    ###########################################################################
    # we really need all of them, so
    scope = SCOPE_ALL
    credential_name = 'classroom-bulk-download-credentials.json'
    ###########################################################################
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, credential_name)
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, scope)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_service(credentials):
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('classroom', 'v1', http=http)
    return service


def get_service_from_scope(scope):
    credentials = get_credentials(scope)
    return get_service(credentials)


def get_drive_service(credentials):
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    return service


def get_drive_service_from_scope(scope):
    credentials = get_credentials(scope)
    return get_drive_service(credentials)


def download_file(drive_service, file_id, filename):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    full_path = os.path.abspath(os.path.expanduser(filename))
    print('Downloading into {}'.format(full_path))
    while done is False:
        status, done = downloader.next_chunk()
        # print("Download {}%.".format(int(status.progress() * 100)))
    with open(filename, 'wb') as f:
        f.write(fh.getvalue())


def response_list(fn, key, **kwargs):
    l = []
    page_token = None
    while True:
        response = fn(pageToken=page_token, **kwargs).execute()
        l.extend(response.get(key,  []))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break
    return l


def response_get(fn, **kwargs):
    response = fn(**kwargs).execute()
    return response


def get_course(course_id):

    service = get_service_from_scope(SCOPE_COURSES)
    fn = service.courses().get
    course = response_get(fn, id=course_id)
    return course


def list_courses():
    service = get_service_from_scope(SCOPE_COURSES)
    courses = response_list(service.courses().list, 'courses', pageSize=100)
    return courses


def get_student(course_id, student_id):
    service = get_service_from_scope(SCOPE_ROSTERS)
    fn = service.courses().students().get
    student = response_get(fn, courseId=course_id, userId=student_id)
    return student


def list_students(course_id):
    # service = get_service_from_scope([SCOPE_ROSTERS, SCOPE_COURSES])
    service = get_service_from_scope(SCOPE_ROSTERS)
    fn = service.courses().students().list
    students = response_list(fn, 'students', courseId=course_id,
                             pageSize=100)
    return students


def get_course_work(course_id, course_work_id):
    service = get_service_from_scope(SCOPE_COURSEWORK)
    fn = service.courses().courseWork().get
    course_work = response_get(fn, id=course_work_id,
                               courseId=course_id)
    return course_work


def list_assignments(course_id):
    service = get_service_from_scope(SCOPE_COURSEWORK)
    fn = service.courses().courseWork().list
    course_works = response_list(fn, 'courseWork', courseId=course_id,
                                 pageSize=100)
    assignments = [cw for cw in course_works if cw['workType'] == ASSIGNMENT]
    return assignments


def list_submissions_for_student(course_id, course_work_id, student_id):
    service = get_service_from_scope(SCOPE_COURSEWORK)
    fn = service.courses().courseWork().studentSubmissions().list
    submissions = response_list(fn, 'studentSubmissions', courseId=course_id,
                                courseWorkId=course_work_id, userId=student_id,
                                pageSize=100)
    return submissions


def list_submissions(course_id, course_work_id):
    service = get_service_from_scope(SCOPE_COURSEWORK)
    fn = service.courses().courseWork().studentSubmissions().list
    submissions = response_list(fn, 'studentSubmissions', courseId=course_id,
                                courseWorkId=course_work_id, pageSize=100)
    return submissions


def download_assignment_submissions(course_id, course_work_id,
                                    course=None, course_work=None,
                                    submissions=None,
                                    assignment_dir=None):
    if course is None:
        course = get_course(course_id)
    if course_work is None:
        course_work = get_course_work(course_id, course_work_id)
    if submissions is None:
        submissions = list_assignments(course_id, course_work_id)
    if assignment_dir is None:
        assignment_dir = get_course_work_dir(course_work, course=course)
    drive_service = get_drive_service_from_scope(SCOPE_DRIVE)
    student_id_dict = create_student_id_dict(course_id)
    os.makedirs(assignment_dir, exist_ok=True)
    for submission in submissions:
        user_id = submission['userId']
        student_name = student_id_dict[user_id]['profile']['name']['fullName']
        download_assignment_submission_files(submission, student_name,
                                             assignment_dir, drive_service)


def download_unreturned_assignment_submissions(course_id, course_work_id,
                                               course=None, course_work=None,
                                               submissions=None,
                                               assignment_dir=None):
    f = download_assignment_submissions_with_state
    f(['RETURNED'], course_id, course_work_id, course, course_work, 
      submissions, assignment_dir, not_matching=True)


def download_turned_in_assignment_submissions(course_id, course_work_id,
                                              course=None, course_work=None,
                                              submissions=None,
                                              assignment_dir=None):
    f = download_assignment_submissions_with_state
    f(['TURNED_IN'], course_id, course_work_id, course, course_work, 
      submissions, assignment_dir, not_matching=True)


def download_assignment_submissions_with_state(states, course_id, 
                                               course_work_id,
                                               course=None, course_work=None,
                                               submissions=None,
                                               assignment_dir=None, 
                                               not_matching=False):
    if course is None:
        course = get_course(course_id)
    if course_work is None:
        course_work = get_course_work(course_id, course_work_id)
    if submissions is None:
        submissions = list_submissions(course_id, course_work_id)
    if assignment_dir is None:
        assignment_dir = get_course_work_dir(course_work, course=course)
        assignment_dir += '--UNRETURNED'
    drive_service = get_drive_service_from_scope(SCOPE_DRIVE)
    student_id_dict = create_student_id_dict(course_id)
    os.makedirs(assignment_dir, exist_ok=True)
    if not_matching:
        new_submissions = [s for s in submissions if s['state'] not in states]
    else:
        new_submissions = [s for s in submissions if s['state'] in states]
    for submission in new_submissions:
        user_id = submission['userId']
        student_name = student_id_dict[user_id]['profile']['name']['fullName']
        try:
            download_assignment_submission_files(submission, student_name,
                                                assignment_dir, drive_service)
        except:
            print('\tCould not download {}\'s file'.format(student_name))
    

def download_submssions_from_student(course_id, course_work_id, student_id,
                                     download_dir=None, drive_service=None):
    if download_dir is None:
        download_dir = get_course_work_dir(course_work, course=course)
    if drive_service is None:
        drive_service = get_drive_service_from_scope(SCOPE_DRIVE)
    student = get_student(course_id, student_id)
    student_name = student['profile']['name']['fullName']
    submissions = list_submissions_for_student(course_id, course_work_id, 
                                               student_id)
    for submission in submissions:
        download_assignment_submission_files(submission, student_name, 
                                             download_dir=download_dir,
                                             drive_service=drive_service)


def download_assignment_submission_files(assignment_submission, student_name,
                                         download_dir, drive_service):
    if 'assignmentSubmission' not in assignment_submission:
        # raise Exception('Attempted to download non-assignment submission')
        print('{} did not have an assignment submission??'.
              format(student_name))
        return
    if 'attachments' not in assignment_submission['assignmentSubmission']:
        print('{} did not include any attachments'.format(student_name))
        return
    attachments = assignment_submission['assignmentSubmission']['attachments']
    # print('attachments: {}\nlen(attachments): {}'.format(attachments,
    #                                                      len(attachments)))
    if not attachments:
        return
    if len(attachments) == 1:
        try:
            download_attachment(attachments[0], student_name, download_dir,
                                drive_service)
        except:
            print('\tCould not download {}\'s file'.format(student_name))
    else:
        for i, attachment in enumerate(attachments):
            try:
                download_attachment(attachment, student_name, download_dir,
                                    drive_service, suffix=i)
            except:
                print('\tCould not download {}\'s file'.format(student_name))


# def download_submission(course_id=None, course_work_id=None, 
                        # submission_id=None, submission=None):


def download_attachment(attachment, student_name, download_dir, drive_service,
                        suffix=None):
    if 'driveFile' not in attachment:
        # raise Exception(
        #     'Cannot download attachment that is not Drive File')
        attachment_type = [k for k in attachment.keys()][0]
        print('{} submitted a {} instead of a drive file'.format(
               student_name, attachment_type))
    drive_file = attachment['driveFile']
    drive_file_id = drive_file['id']
    drive_file_name = drive_file['title']
    filename = get_drive_file_download_filename(drive_file, student_name,
                                                suffix)
    filepath = os.path.join(download_dir, filename)
    print('Downloading {}\'s file: {}'.format(student_name, drive_file_name))
    download_file(drive_service, drive_file_id, filepath)


def get_course_from_user():
    courses = list_courses()

    def course_full_name(course):
        return '{} {}'.format(course['name'], course['section'])
    return get_choice_from_user(courses, course_full_name,
                                title='Courses')


def get_assignment_from_user(course_id):
    assignments = list_assignments(course_id)

    def assignment_name(course):
        return course['title']
    return get_choice_from_user(assignments, assignment_name,
                                title='Assignments')


def get_choice_from_user(choices, strf, title=None):
    while True:
        if title is not None:
            print('{}:'.format(title))
        for i, choice in enumerate(choices):
            print('\t{}: {}'.format(i+1, strf(choice)))
        print('Enter the index of the choice you want:')
        try:
            choice_index = int(input())
            if choice_index not in range(1, len(choices)+1):
                print('Not in range, try again')
            else:
                break
        except ValueError:
            print('Not a number, try again')
        print('Press Ctrl-C to exit')
    return choices[choice_index-1]


def course_full_name(course):
    return '{}-{}'.format(course['name'], course['section'])


def create_student_id_dict(course_id=None, students=None):
    if course_id is None and students is None:
        raise Exception('Need course_id or students')
    if students is None:
        students = list_students(course_id)
    student_id_dict = {}
    for student in students:
        student_id_dict[student['userId']] = student
    return student_id_dict


def get_download_dir(root_dir=None, shorten=False):
    if root_dir is None:
        return os.path.join('.', DOWNLOAD_DIR)
    return root_dir


def get_course_dir(course, root_dir=None, shorten=False):
    course_name = course_full_name(course)
    course_dir_name = make_string_safe_filename(course_name)
    course_dir = os.path.join(get_download_dir(root_dir=root_dir, 
                                               shorten=shorten), 
                              course_dir_name)
    # os.makedirs(course_dir, exist_ok=True)
    return course_dir


def get_course_work_dir(course_work, course=None, timeStamp=True, 
                        root_dir=None, shorten=False):
    if course is None:
        course_id = course_work['courseId']
        course = get_course(course_id)
    course_dir = get_course_dir(course, root_dir=root_dir, shorten=shorten)
    course_work_title = course_work['title']
    course_work_dir = make_string_safe_filename(course_work_title)
    course_work_dir = os.path.join(course_dir, course_work_dir)
    if timeStamp:
        import datetime
        stamp = make_datetime_str(datetime.datetime.now())
        dir_name = '{}'.format(stamp)
        course_work_dir = os.path.join(course_work_dir, dir_name)
    return course_work_dir


def get_drive_file_download_filename(drive_file, student_name, suffix=None):
    if suffix is not None:
        student_name = '{}--{:02}'.format(student_name, suffix)
    drive_file_name, drive_file_ext = os.path.splitext(drive_file['title'])
    # return '{}--{}'.format(student_name, drive_file_name)
    return student_name + drive_file_ext


def make_string_safe_filename(s):
    keep_characters = '-_.'
    return ''.join([c for c in s.replace(' ', '_')
                    if c.isalnum() or c in keep_characters])
    # keep_characters = ' -_.'

    # def replace_bad_chars(c):
    #     if c.isalnum() or c in keep_characters:
    #         return c
    #     else:
    #         return '_'
    # # schars = [c for c in s if c.isalnum() or c in keep_characters]
    # schars = [replace_bad_chars(c) for c in s]
    # return ''.join(schars).rstrip()


def make_datetime_str(dt):
    return '{:%Y-%m-%d_%H-%M-%S}'.format(dt)


def parse_google_datetime(dt_string):
    from datetime import datetime
    return datetime.strptime(dt_string, 'Y-%m-%dT%H:%M:%S.%fZ')
