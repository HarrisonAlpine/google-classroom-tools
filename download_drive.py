#!/usr/bin/env python

from googlehelper import *
import json

credentials = get_credentials(SCOPE_DRIVE)
service = get_drive_service(credentials)

page_token = None

results = service.files().list(
   pageSize=10, fields="nextPageToken, files(id, name)").execute()

items = results.get('files', [])

if not items:
    print('No files found.')
else:
    print('Files:')
    for item in items:
        print('{0} ({1})'.format(item['name'], item['id']))
