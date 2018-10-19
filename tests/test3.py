#!/usr/bin/python
# coding: utf_8


import modules as tm


osf = u'Аудит'
name = u'Просмотр аудита и ограниченный просмотр аудита'
osfNum = 1
num = 3
stages = 1
params = ['firstUserName']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()
    test.runCmdFirstUser(cmd='cat /var/log/audit/audit.log', code=1)
    test.runCmdFirstUser(cmd='cat /var/log/secure', code=1)
    test.runCmdFirstUser(cmd='cat /var/log/maillog', code=1)
    test.runCmdFirstUser(cmd='cat /var/log/messages', code=1)

    test.runCmdFromRoot(cmd='cat /var/log/audit/audit.log', code=0)
    test.runCmdFromRoot(cmd='cat /var/log/secure', code=0)
    test.runCmdFromRoot(cmd='cat /var/log/maillog', code=0)
    test.runCmdFromRoot(cmd='cat /var/log/messages', code=0)

    test.runCmdFirstUser(cmd='aureport -au', code=1)
    test.runCmdFromRoot(cmd='aureport -au', code=0)


except Exception as e:
    test.showError(e.message)


finally:
    # result out--------------------------------------------------------------------------------------------------------
    test.showResultBlock()



