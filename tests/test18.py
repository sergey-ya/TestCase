#!/usr/bin/python
# coding: utf_8

import modules as tm



osf = u'Защита данных пользователя'
name = u'Уничтожение информации'
osfNum = 2
num = 18
stages = 1
params = ['firstUserName', 'testDir']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
testDir = test.params['testDir']

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    test.runCmdFromRoot(cmd="chmod 777 %s" % testDir, code=0)

    test.runCmdFirstUser(cmd="touch %s/srm.file" % testDir, code=0)
    test.runCmdFirstUser(cmd="touch %s/shred.file" % testDir, code=0)
    test.runCmdFirstUser(cmd="touch %s/wipe.file" % testDir, code=0)
    test.runCmdFirstUser(cmd="mkdir %s/wipe" % testDir, code=0)


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    test.runCmdFirstUser(cmd="srm %s/srm.file" % testDir, code=0)
    test.runCmdFirstUser(cmd="shred --iteration=30 %s/shred.file" % testDir, code=0)
    test.runCmdFirstUser(cmd="wipe -Q 25 -f %s/wipe.file" % testDir, code=0)
    test.runCmdFirstUser(cmd="wipe -Q 10 -r -f %s/wipe/" % testDir, code=0)


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
