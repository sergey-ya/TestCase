#!/usr/bin/python
# coding: utf_8

import os, shutil, pwd
import time
from datetime import datetime
import socket
import modules as tm



osf = u'Аудит'
name = u'Действия в случае возможной потери данных аудита'
osfNum = 1
num = 7
stages = 1
params = ['firstUserName']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']

file1 = '/etc/audit/auditd.conf'
file2 = '/var/spool/mail/root'

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()
    test.createCopyFile(file1)



    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    st = os.statvfs("/home")
    du = st.f_bsize * st.f_bavail / 1024 / 1024
    du = du + 1000

    tm.changeRowFile(path=file1, oldRow='space_left =', newRow='space_left = %s' % str(du), start=True)
    tm.changeRowFile(path=file1, oldRow='space_left_action =', newRow='space_left_action = EMAIL', start=True)
    tm.changeRowFile(path=file1, oldRow='action_mail_acct =',
                     newRow='action_mail_acct = root', start=True)
    test.showActionMsg('change data to file %s' % file1)

    test.runCmdFromRoot(cmd='service auditd restart', code=0)
    time.sleep(3)

    f = open(file2, "r+")
    rows = f.readlines()
    f.close()

    today = datetime.today()

    status = False
    for ind, row in enumerate(rows):
        row = row.replace(' ', '')

        findText1 = 'Subject:AuditDiskSpaceAlert'
        findText2 = 'Date: ' + today.strftime("%a, %d %b %Y ").replace(' 0', '  ')
        findText2 = findText2 + today.strftime("%H:")

        if row.find(findText1) == 0:
            if rows[ind + 2].find(findText2) == 0:
                status = True

    if not status:
        test.addResult(msg=u'Не найдено извещение о превышении заданного порога минимально необходимого пространства для'
                           u' записи журналов.',
                       wait='param1:%s, param2:%s' % (findText1, findText2),
                       taken='file /var/spool/mail/root')


except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()
        test.exchangeCopyFile(file1)

        test.runCmdFromRoot(cmd='service auditd restart', code=0, remov=True)

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()
