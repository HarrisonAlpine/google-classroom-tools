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

SCOPE_COURSES = 'https://www.googleapis.com/auth/classroom.courses.readonly'
CREDENTIAL_COURSES = 'classroom.googleapis.com-courses.json'
SCOPE_COURSEWORK = 'https://www.googleapis.com/auth/classroom.coursework.students.readonly'
CREDENTIAL_COURSEWORK = 'classroom.googleapis.com-coursework.json'
SCOPE_ROSTERS = 'https://www.googleapis.com/auth/classroom.rosters.readonly'
CREDENTIAL_ROSTERS = 'classroom.googleapis.com-rosters.json'
SCOPE_STUDENT_SUBMISSIONS = 'https://www.googleapis.com/auth/classroom.student-submissions.students.readonly'
CREDENTIAL_STUDENT_SUBMISSIONS = 'classroom.googleapis.com-student-submissions.json'

SCOPE_DRIVE = 'https://www.googleapis.com/auth/drive.readonly'

SCOPE_ALL = [SCOPE_COURSES,
             SCOPE_COURSEWORK,
             SCOPE_ROSTERS,
             SCOPE_STUDENT_SUBMISSIONS,
             SCOPE_DRIVE]
CREDENTIAL_ALL = 'classroom.googleapis.com-all.json'
CREDENTIAL_MULTIPLE = 'classroom.googleapis.com-multiple.json'

CREDENTIAL_FROM_SCOPE = {
    SCOPE_COURSES: CREDENTIAL_COURSES,
    SCOPE_COURSEWORK: CREDENTIAL_COURSEWORK,
    SCOPE_ROSTERS: CREDENTIAL_ROSTERS,
    SCOPE_STUDENT_SUBMISSIONS: CREDENTIAL_STUDENT_SUBMISSIONS,
    SCOPE_DRIVE: 'drive.json'}


DOWNLOAD_DIR = 'downloads'
JSON_DIR = 'json'
TXT_DIR = 'txt'

def get_credentials(scope):
    if type(scope) is str:
        if scope not in CREDENTIAL_FROM_SCOPE:
            raise Exception('Scope (' + scope + ') is invalid.')
        credential_name = CREDENTIAL_FROM_SCOPE[scope]
    else:
        for s in scope:
            if s not in CREDENTIAL_FROM_SCOPE:
                raise Exception('Scope "' + s + '" was invalid.')
        credential_name = CREDENTIAL_MULTIPLE
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


def download_file(drive_service, file_id, filename):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with open(filename, 'wb') as f:
        f.write(fh.getvalue())


def download_response_list(fn, key, **kwargs):
    l = []
    page_token = None
    while True:
        response = fn(pageToken=page_token, **kwargs).execute()
        l.extend(response.get(key,  []))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break
    return l


def download_response_get(fn, **kwargs):
    response = fn(**kwargs).execute()
    return response


def download_course(course_id):

    service = get_service_from_scope(SCOPE_COURSES)
    fn = service.courses().get
    course = download_response_get(fn, id=course_id)
    return course


def download_courses():
    service = get_service_from_scope(SCOPE_COURSES)
    courses = download_response_list(service.courses().list,
                                     'courses',
                                     pageSize=100)
    return courses


def download_students(course_id):
    # service = get_service_from_scope([SCOPE_ROSTERS, SCOPE_COURSES])
    service = get_service_from_scope(SCOPE_ROSTERS)
    fn = service.courses().students().list
    students = download_response_list(fn, 'students', courseId=course_id,
                                      pageSize=100)
    return students


def download_assignments(course_id):
    service = get_service_from_scope(SCOPE_COURSEWORK)
    fn = service.courses().courseWork().list
    assignments = download_response_list(fn, 'courseWork', 
                                         courseId=course_id,
                                         pageSize=100)
    return assignments


def download_course_work(course_id, course_work_id):
    service = get_service_from_scope(SCOPE_COURSEWORK)
    fn = service.courses().courseWork().get
    course_work = download_response_get(fn, id=course_work_id,
                                        courseId=course_work_id)
    return course_work


def download_submissions(course_id, submission_id):
    service = get_service_from_scope(SCOPE_COURSEWORK)
    drive_credentials = get_credentials(SCOPE_DRIVE)
    drive_service = get_drive_service(drive_credentials)
    students = download_students(course_id)
    student_dict = {}
    for student in students:
        student_dict[student['userId']] = \
            student['profile']['name']['fullName']
    fn = service.courses().courseWork().studentSubmissions().list
    # kwargs = {'courseId': course_id,
              # 'courseWorkId': course_work_id,
              # 'pageSize': 100}
    submissions = download_response_list(fn,
                                         'studentSubmissions',
                                         courseId=course_id,
                                         courseWorkId=course_work_id,
                                         pageSize=100)
    return submissions


def get_course_from_user():
    courses = download_courses()
    print('Courses:')
    while True:
        for i, course in enumerate(courses):
            print('\t{}: {}'.format(i+1, course_full_name(course)))
        print('Enter the index of the course you want:')
        try:
            choice_index = int(input())
            if choice_index not in range(1, len(courses)+1):
                print('Not in range, try again')
            else:
                break
        except ValueError:
            print('Not a number, try again')
        print('Press Ctrl-C to exit')
    return courses[choice_index-1]
    
    
    
def course_full_name(course):
    return '{} {}'.format(course['name'], course['section'])


def get_course_dir(course):
    course_name = course_full_name(course)
    course_dir_name = make_string_safe_filename(course_name)
    course_dir = os.path.join(DOWNLOAD_DIR, course_dir_name)
    # os.makedirs(course_dir, exist_ok=True)
    return course_dir


def get_course_work_dir(course_work, course=None, timeStamp=True):
    if course is None:
        course_id = course_work['courseId']
        course = download_course(course_id)
    course_dir = get_course_dir(course)
    course_work_title = course_work['title']
    course_work_dir = os.path.join(course_dir, course_work_title)
    if timeStamp:
        import datetime
        stamp = make_datetime_str(datetime.datetime.now())
        dir_name = 'Downloaded {}'.format(stamp)
        course_work_dir = os.path.join(course_work_dir, dir_name)
    return course_work_dir


def get_drive_file_download_filename(drive_file, student):
    student_name = student['profile']['name']['fullName']
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
