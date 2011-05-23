# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# internal #
import os
from datetime import datetime
from getpass import getpass

# external #
from simpledropbox import SimpleDropbox, SdFile

def update():
    local_path = './docs'
    remote_path = '/Public/Diploma'
    file_name = '/msts.docx'
    tz = 'Europe/Moscow'

    db_user = raw_input('Login: ')
    db_pass = getpass('Password: ')

    if raw_input('Update from remote [y/n]? ') == ('y' or 'Y'): download = True
    else: download = False

    sdb = SimpleDropbox(db_user, db_pass, tz)
    sdb.login()

    files = sdb.ls(remote_path, filter=SdFile)

    if not download:
        # uploading
        output = open(local_path + file_name, 'rb')
        sdb.put(remote_path + file_name, output)      #NB: use of ./ results in 404 error
        output.close()

        print '\nUploaded %s (%d) %s' % (
            os.path.basename(file_name),
            os.path.getsize(local_path + file_name),
            datetime.fromtimestamp( os.path.getmtime(local_path + file_name) ),
        )
    else:
        if not files: print '\nNo files to update from!'
        for file in files:
            if os.path.basename(file_name) == os.path.basename(file.path):
                # downloading
                inf, data = sdb.get(file)
                output = open(local_path + file_name, 'wb')
                output.write(data)
                output.close()

                print '\nUpdated %s (%d) %s' % (
                    os.path.basename(file_name),
                    os.path.getsize(local_path + file_name),
                    datetime.fromtimestamp( os.path.getmtime(local_path + file_name)),
                )
    raw_input('\nAny key to proceed.')

if __name__ == '__main__':
    try:
        update()
    except Exception, e:
        print e