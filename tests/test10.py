#!/usr/bin/python
# coding: utf_8

import os, shutil
import modules as tm



osf = u'Защита данных пользователя'
name = u'Дискреционное управление доступом — ACL'
osfNum = 2
num = 10
stages = 1
params = ['firstUserName', 'secondUserName', 'testDir']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
secondUser = test.params['secondUserName']
testDir = test.params['testDir']

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    def runAnalis(r=1, w=1, u_name=None):
        test.runCmdFromUser(user=u_name, cmd="cat %s/acl_root.txt" % testDir, code=r)
        test.runCmdFromUser(user=u_name, cmd="echo '123' >> %s/acl_root.txt" % testDir, code=w)

    test.runCmdFromRoot(cmd="touch %s/acl_root.txt" % testDir, code=0)
    test.runCmdFromRoot(cmd="chmod 660 %s/acl_root.txt" % testDir, code=0)

    runAnalis(u_name=firstUser)
    runAnalis(u_name=secondUser)

    test.runCmdFromRoot(cmd="setfacl -m u:%s:r-- %s/acl_root.txt" % (firstUser, testDir), code=0)
    test.runCmdFromRoot(cmd="setfacl -m g:%s:-w- %s/acl_root.txt" % (secondUser, testDir), code=0)

    runAnalis(u_name=firstUser, r=0)
    runAnalis(u_name=secondUser, w=0)


except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()

