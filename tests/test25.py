#!/usr/bin/python
# coding: utf_8

import modules as tm



osf = u'Идентификация и аутентификация'
name = u'Аутентификация до любых действий пользователя'
osfNum = 3
num = 25
stages = 1
params = ['firstUserName', 'sshHostName', 'sshUserName', 'sshPasswd']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
sshHost = test.params['sshHostName']
sshUser = test.params['sshUserName']
sshPasswd = test.params['sshPasswd']

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()
    test.runCmdFromRoot(cmd='id %s' % firstUser, code=0)
    test.runCmdFirstUser(cmd='id %s' % firstUser, code=0)

    test.sshConnect(host=sshHost, user=sshUser, passwd=sshPasswd)
    test.sshRunCmd(cmd='id', code=0)
    test.sshDisconnect()


except Exception as e:
    test.showError(e.message)



finally:
    # result out--------------------------------------------------------------------------------------------------------
    test.showResultBlock()



