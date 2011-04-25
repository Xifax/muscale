# -*- coding: utf-8 -*-
__author__ = 'Yadavito'

# internal #
import os
from datetime import datetime
from getpass import getpass
#import pytz

# external #
from simpledropbox import SimpleDropbox, SdFile

def update():
    #TODO: check if exists, if not - create
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
        if len(files) == 0: print '\nNo files to update from!'
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

#    est = pytz.timezone(tz)

#   if len(files) == 0:
#       pass
#   else:
#       for file in files:
#           if file_name.split('/')[-1:] == file.path.split('\\')[-1:]:
#               sdf = sdb.stat(file)
#               local_mod = toUTCc( datetime.fromtimestamp( os.path.getmtime(local_path + file_name) ), est )
#
#               if sdf.modified > local_mod:
#                   print '(remote) %s (%d): %s\t>>>\t\t(local) %s (%d): %s' % (
#                   # remote
#                   os.path.basename(sdf.path),
#                   sdf.size,
#                   sdf.modified.astimezone(est).strftime('%Y-%m-%d %H:%M:%S'),
#                   # local
#                   os.path.basename(file_name),
#                   os.path.getsize(local_path + file_name),
#                   datetime.fromtimestamp( os.path.getmtime(local_path + file_name) )
#                   )
#
#                   # downloading
#                   inf, data = sdb.get(file)
#                   output = open(local_path + file_name, 'wb')
#                   output.write(data)
#                   output.close()
#               else:
#                   print '(remote) %s (%d): %s\t<<<\t\t(local) %s (%d): %s' % (
#                   # remote
#                   os.path.basename(sdf.path),
#                   sdf.size,
#                   sdf.modified.astimezone(est).strftime('%Y-%m-%d %H:%M:%S'),
#                   # local
#                   os.path.basename(file_name),
#                   os.path.getsize(local_path + file_name),
#                   datetime.fromtimestamp( os.path.getmtime(local_path + file_name) )
#                   )
#
#                   # uploading
#                   output = open(local_path + file_name, 'rb')
#                   sdb.put(remote_path + file_name, output)      #NB: use of ./ results in 404 error
#                   output.close()

#def toUTCc(date, tz):
#    return tz.normalize(tz.localize(date)).astimezone(pytz.utc)

if __name__ == '__main__':
    try:
        update()
    except Exception, e:
        print e