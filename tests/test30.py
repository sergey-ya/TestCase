#!/usr/bin/python
# coding: utf_8


import modules as tm



osf = u'Идентификация и аутентификация'
name = u'Идентификация объектов доступа'
osfNum = 3
num = 30
stages = 1
params = ['firstUserName', 'mntDevice']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
mntDevice = test.params['mntDevice']

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()
    test.runCmdFirstUser(cmd="ls -ial /dev/",  code=0)
    test.runCmdFirstUser(cmd="ls -l %s -uuid" % mntDevice, code=0)
    test.runCmdFirstUser(cmd="ls -il /home/%s/" % firstUser, code=0)
    test.runCmdFirstUser(cmd="ps aux", code=0)
    test.runCmdFirstUser(cmd="lspci", code=0)

    res = test.runCmdFirstUser(cmd="lsusb")['code']
    if res != 0 and res != 1:
        test.addResult(msg='lsusb access error', wait='code: 0 or 1', taken='code: %s' % res)


except Exception as e:
    test.showError(e.message)


finally:
    # result out--------------------------------------------------------------------------------------------------------
    test.showResultBlock()

