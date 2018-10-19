#!/usr/bin/python
# coding: utf_8

import modules as tm


osf = u'Защита ОО'
name = u'Управление доступом к компонентам ОС'
osfNum = 5
num = 40
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

    test.runCmdFirstUser(cmd='ls -l /etc/', code=0)
    test.runCmdFirstUser(cmd='echo "123" >> /etc/hosts', code=1)
    test.runCmdFirstUser(cmd='cat /var/log/secure', code=1)
    test.runCmdFirstUser(cmd='cat /var/log/messages', code=1)
    test.runCmdFirstUser(cmd='ausearch -ua 500 -i', code=1)


except Exception as e:
    test.showError(e.message)


finally:
    # result out--------------------------------------------------------------------------------------------------------
    test.showResultBlock()
