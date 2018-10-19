#!/usr/bin/python
# coding: utf_8


from datetime import datetime
import socket, time
import modules as tm



osf = u'Аудит'
name = u'Генерация данных аудита'
osfNum = 1
num = 2
stages = 1
params = ['firstUserName']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']

file1 = '/var/log/audit/audit.log'
file2 = '/var/log/secure'
file3 = '/var/log/maillog'
file4 = '/var/log/messages'

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()


    now = datetime.now()
    currDate = now.strftime("%b %d ").replace(' 0', '  ')
    currDate = currDate + now.strftime("%H:")

    test.sshConnect(host='127.0.0.1', user=firstUser, passwd='qqqwww')
    test.sshDisconnect()

    test.runCmdFirstUser(cmd='echo "test" | sendmail root@%s' % socket.gethostname(), code=0)

    time.sleep(3)

    test.runCmdFromRoot(cmd="cat %s | grep -E 'type=USER_AUTH.*acct=\"%s\".*addr=127.0.0.1'" %
                            (file1, firstUser), code=0)

    test.runCmdFromRoot(cmd='cat %s | grep -E "%s.*Accepted password for %s from 127.0.0.1"' %
                            (file2, currDate, firstUser), code=0)

    test.runCmdFromRoot(cmd="cat %s | grep -E '%s.*from=<%s@%s'" %
                            (file3, currDate, firstUser, socket.gethostname()), code=0)

    test.runCmdFromRoot(cmd='cat %s | grep -E "%s.*Starting Session.*%s"' %
                            (file4, currDate, firstUser), code=0)

except Exception as e:
    test.showError(e.message)


finally:
    # result out--------------------------------------------------------------------------------------------------------
    test.showResultBlock()
