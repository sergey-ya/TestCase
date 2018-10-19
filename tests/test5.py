#!/usr/bin/python
# coding: utf_8

import os, shutil
import time
import modules as tm


osf = u'Аудит'
name = u'Избирательный аудит'
osfNum = 1
num = 5
stages = 1
params = ['firstUserName']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']

file1 = '/var/log/audit/audit.log'
auditRules = []

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    test.createCopyFile(file1)

    auditRules = test.runCmdFromRoot(cmd='auditctl -l', code=0)['output'].split('\n')


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    test.runCmdFromRoot(cmd='auditctl -D', code=0)
    test.runCmdFirstUser(cmd='mkdir /home/%s/audit_create_dir2' % firstUser, code=0)
    test.runCmdFirstUser(cmd='rmdir /home/%s/audit_create_dir2' % firstUser, code=0)
    test.runCmdFromRoot(cmd='cat /var/log/audit/audit.log | grep audit_create_dir2', code=1)

    test.runCmdFromRoot(cmd='auditctl -a entry,always -S mkdir -S rmdir', code=0)
    test.runCmdFirstUser(cmd='mkdir /home/%s/audit_create_dir2' % firstUser, code=0)
    test.runCmdFirstUser(cmd='rmdir /home/%s/audit_create_dir2' % firstUser, code=0)


    test.runCmdFromRoot(cmd='cat /var/log/audit/audit.log | grep audit_create_dir2', code=0)


except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()


        test.runCmdFromRoot(cmd='auditctl -D', code=0, remov=True)
        for elem in auditRules:
            if elem != 'No rules':
                rules = test.runCmdFromRoot(cmd='auditctl %s' % elem, code=0, remov=True)

        test.exchangeCopyFile(file1)

        test.runCmdFromRoot(cmd='service auditd restart', code=0, remov=True)


    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()






