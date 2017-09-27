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
# CLASSROOM_CREDENTIALS_PREFIX = 'classroom.googleapis.com'
# DRIVE_CREDENTIALS_PREFIX = 'drive.googleapis.com'

SCOPE_COURSES = SCOPE_PREFIX + 'classroom.courses.readonly'
# CREDENTIAL_COURSES = CLASSROOM_CREDENTIALS_PREFIX + '-courses.json'
SCOPE_COURSEWORK = SCOPE_PREFIX + 'classroom.coursework.students.readonly'
# CREDENTIAL_COURSEWORK = CLASSROOM_CREDENTIALS_PREFIX + '-coursework.json'
SCOPE_ROSTERS = SCOPE_PREFIX + 'classroom.rosters.readonly'
# CREDENTIAL_ROSTERS = CLASSROOM_CREDENTIALS_PREFIX + '-rosters.json'
SCOPE_STUDENT_SUBMISSIONS = SCOPE_PREFIX + \
                            'classroom.student-submissions.students.readonly'
# CREDENTIAL_STUDENT_SUBMISSIONS = CLASSROOM_CREDENTIALS_PREFIX + \
#                                  '-student-submissions.json'
SCOPE_DRIVE = SCOPE_PREFIX + 'drive.readonly'
# CREDENTIAL_DRIVE = DRIVE_CREDENTIALS_PREFIX + '-drive.json'

SCOPE_ALL = [SCOPE_COURSES,
             SCOPE_COURSEWORK,
             SCOPE_ROSTERS,
             SCOPE_STUDENT_SUBMISSIONS,
             SCOPE_DRIVE]
# CREDENTIAL_ALL = CLASSROOM_CREDENTIALS_PREFIX + '-all.json'
# CREDENTIAL_MULTIPLE = CLASSROOM_CREDENTIALS_PREFIX + '-multiple.json'

CREDENTIALS_SUFFIX = '-credentials.json'

def safe_name_from_scope(scope):
    return scope.rsplit('/', 1)[-1]

def credentials_file_from_scope(scope):
    return safe_name_from_scope(scope) + CREDENTIALS_SUFFIX

def credentials_file_from_scopes(scopes):
    return '-'.join([safe_name_from_scope(s) for s in scopes]) + \
        CREDENTIALS_SUFFIX

# CREDENTIAL_FROM_SCOPE = {
#     SCOPE_COURSES: CREDENTIAL_COURSES,
#     SCOPE_COURSEWORK: CREDENTIAL_COURSEWORK,
#     SCOPE_ROSTERS: CREDENTIAL_ROSTERS,
#     SCOPE_STUDENT_SUBMISSIONS: CREDENTIAL_STUDENT_SUBMISSIONS,
#     SCOPE_DRIVE: CREDENTIAL_DRIVE}

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
    ############################################################################
    # we really need all of them, so
    scope = SCOPE_ALL
    credential_name = 'classroom-bulk-download-credentials.json'
    ############################################################################
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
    # print('Downloading into {}'.format(filename))
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


def list_submissions(course_id, course_work_id):
    service = get_service_from_scope(SCOPE_COURSEWORK)
    fn = service.courses().courseWork().studentSubmissions().list

    submissions = response_list(fn, 'studentSubmissions', courseId=course_id,
                                courseWorkId=course_work_id, pageSize=100)
    return submissions


def download_assignment_submissions(course_id, course_work_id,
                                    course=None, course_work=None,
                                    assignment_submissions=None):
    if course is None:
        course = get_course(course_id)
    if course_work is None:
        course_work = get_course_work(course_id, course_work_id)
    drive_service = get_drive_service_from_scope(SCOPE_DRIVE)
    if assignment_submissions is None:
        assignment_submissions = list_assignments(course_id, course_work_id)
    student_id_dict = create_student_id_dict(course_id)
    course_work_dir = get_course_work_dir(course_work, course=course)
    os.makedirs(course_work_dir, exist_ok=True)
    for assignment_submission in assignment_submissions:
        user_id = assignment_submission['userId']
        student_name = student_id_dict[user_id]['profile']['name']['fullName']
        download_assignment_submission_files(assignment_submission,
                                             student_name, course_work_dir,
                                             drive_service)


def download_assignment_submission_files(assignment_submission, student_name,
                                         download_dir, drive_service):
    if 'assignmentSubmission' not in assignment_submission:
        # raise Exception('Attempted to download non-assignment submission')
        print('{} did not have an assignment submission??'.format(student_name))
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
        download_attachment(attachments[0], student_name, download_dir,
                            drive_service)
    else:
        for i, attachment in enumerate(attachments):
            download_attachment(attachment, student_name, download_dir,
                                drive_service, suffix=i)


def download_attachment(attachment, student_name, download_dir, drive_service,
                        suffix=None):
    if 'driveFile' not in attachment:
        # raise Exception('Cannot download attachment that is not a Drive File')
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
    return '{} {}'.format(course['name'], course['section'])


def create_student_id_dict(course_id=None, students=None):
    if course_id is None and students is None:
        raise Exception('Need course_id or students')
    if students is None:
        students = list_students(course_id)
    student_id_dict = {}
    for student in students:
        student_id_dict[student['userId']] = student
    return student_id_dict


def get_download_dir():
    return os.path.join('.', DOWNLOAD_DIR)


def get_course_dir(course):
    course_name = course_full_name(course)
    course_dir_name = make_string_safe_filename(course_name)
    course_dir = os.path.join(get_download_dir(), course_dir_name)
    # os.makedirs(course_dir, exist_ok=True)
    return course_dir


def get_course_work_dir(course_work, course=None, timeStamp=True):
    if course is None:
        course_id = course_work['courseId']
        course = get_course(course_id)
    course_dir = get_course_dir(course)
    course_work_title = course_work['title']
    course_work_dir = os.path.join(course_dir, course_work_title)
    if timeStamp:
        import datetime
        stamp = make_datetime_str(datetime.datetime.now())
        dir_name = 'Downloaded {}'.format(stamp)
        course_work_dir = os.path.join(course_work_dir, dir_name)
    return course_work_dir


def get_drive_file_download_filename(drive_file, student_name, suffix=None):
    if suffix is not None:
        student_name = '{}--{:02}'.format(student_name, suffix)
    drive_file_name = drive_file['title']
    return '{}--{}'.format(student_name, drive_file_name)


def make_string_safe_filename(s):
    keep_characters = ' -_.'
    def replace_bad_chars(c):
        if c.isalnum() or c in keep_characters:
            return c
        else:
            return '_'
    # schars = [c for c in s if c.isalnum() or c in keep_characters]
    schars = [replace_bad_chars(c) for c in s]
    return ''.join(schars).rstrip()


def make_datetime_str(dt):
    return '{:%Y-%m-%d_%H-%M-%S}'.format(dt)
