#!/usr/bin/python
# coding: utf_8

import os, shutil
import modules as tm



osf = u'Аудит'
name = u'Защищенное хранение журнала аудита'
osfNum = 1
num = 6
stages = 1
params = ['firstUserName']
progress = '2/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    def runRemove(file=None):
        test.createCopyFile(file)
        test.runCmdFromRoot(cmd='rm %s -f' % file, code=0)
        test.exchangeCopyFile(file)


    def runEdit(file=None):
        test.createCopyFile(file)
        test.runCmdFromRoot(cmd='echo "123" >> %s' % file, code=0)
        test.exchangeCopyFile(file)

    test.runCmdFirstUser(cmd='rm /var/log/audit/audit.log -f', code=1)
    test.runCmdFirstUser(cmd='rm /var/log/secure -f', code=1)
    test.runCmdFirstUser(cmd='rm /var/log/maillog -f', code=1)
    test.runCmdFirstUser(cmd='rm /var/log/messages -f', code=1)
    # test.runCmdFirstUser(cmd='rm /var/log/iptables', code=1)

    runRemove('/var/log/audit/audit.log')
    runRemove('/var/log/secure')
    runRemove('/var/log/maillog')
    runRemove('/var/log/messages')
    # runAnalis('/var/log/iptables')



    test.runCmdFirstUser(cmd='echo "123" >> /var/log/audit/audit.log', code=1)
    test.runCmdFirstUser(cmd='echo "123" >> /var/log/secure', code=1)
    test.runCmdFirstUser(cmd='echo "123" >> /var/log/maillog', code=1)
    test.runCmdFirstUser(cmd='echo "123" >> /var/log/messages', code=1)
    # test.runCmdFirstUser(cmd='rm /var/log/iptables', code=1)

    runEdit('/var/log/audit/audit.log')
    runEdit('/var/log/secure')
    runEdit('/var/log/maillog')
    runEdit('/var/log/messages')
    # runEdit('/var/log/iptables')

except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.runCmdFromRoot(cmd='service auditd restart', code=0, remov=True)
        test.runCmdFromRoot(cmd='systemctl restart rsyslog', code=0, remov=True)

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()



