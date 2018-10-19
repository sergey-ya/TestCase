#!/usr/bin/python
# coding: utf_8

import modules as tm



osf = u'Идентификация и аутентификация'
name = u'Определение атрибутов пользователя'
osfNum = 3
num = 23
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

    test.runCmdFirstUser(cmd="id", code=0)
    test.runCmdFirstUser(cmd="id -un", code=0)
    test.runCmdFirstUser(cmd="id -unr", code=0)
    test.runCmdFirstUser(cmd="groups", code=0)

    test.runCmdFromRoot(cmd="cat /etc/passwd", code=0)
    test.runCmdFromRoot(cmd="cat /etc/group", code=0)
    test.runCmdFromRoot(cmd="cat /etc/shadow", code=0)

    test.runCmdFromRoot(cmd="semanage login -l", code=0)
    test.runCmdFromRoot(cmd="semanage user -l", code=0)


except Exception as e:
    test.showError(e.message)


finally:
    # result out--------------------------------------------------------------------------------------------------------
    test.showResultBlock()
