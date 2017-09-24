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
