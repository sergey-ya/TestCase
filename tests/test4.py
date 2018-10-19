#!/usr/bin/python
# coding: utf_8

from datetime import datetime
import time
import modules as tm



osf = u'Аудит'
name = u'Выборочный просмотр аудита'
osfNum = 1
num = 4
stages = 1
params = ['firstUserName', 'secondUserName']
progress = '2/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()
    firstUserID = test.runCmdFromRoot(cmd='id -u %s' % firstUser, code=0)['output'].rstrip()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    test.runCmdFromRoot(cmd='cat /var/log/secure', code=0)
    today = datetime.today()
    # test.runCmdFromRoot(cmd='cat /var/log/secure | grep "%s"' % today.strftime("%b %-d"), out='ok', code=0)
    test.runCmdFromRoot(cmd='cat /var/log/secure', code=0)
    test.runCmdFromRoot(cmd='cat /var/log/audit/audit.log', code=0)

    test.runCmdSecondUser(cmd="echo 'qqqwww' | su %s" % firstUser, code=0)
    time.sleep(3)
    test.runCmdFromRoot(cmd='cat /var/log/audit/audit.log | grep -E "uid=%s|type=USER_AUTH"' % firstUserID, code=0)

    # test.runCmdFromRoot(cmd="cat /var/log/audit/audit.log | grep -E 'acct=\"%s\".*res=success'" % firstUser, out='ok', code=0)
    test.runCmdFromRoot(cmd="cat /var/log/audit/audit.log | grep -E 'acct=\"root\".*res=success'", code=0)
    test.runCmdFromRoot(cmd="cat /var/log/audit/audit.log | grep -E 'type=USER_START.*res=success'", code=0)

    test.runCmdFromRoot(cmd="sort -k4 /var/log/audit/audit.log", code=0)

    test.runCmdFromRoot(cmd="ausearch -ui 0", code=0)


except Exception as e:
    test.showError(e.message)


finally:
    # result out--------------------------------------------------------------------------------------------------------
    test.showResultBlock()


