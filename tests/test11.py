#!/usr/bin/python
# coding: utf_8

import modules as tm



osf = u'Защита данных пользователя'
name = u'Дискреционное управление доступом — дополнительные правила'
osfNum = 2
num = 11
stages = 1
params = ['mntDevice', 'testDir']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
testDir = test.params['testDir']
mntDevice = test.params['mntDevice']

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()
    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт а')
    test.runCmdFromRoot(cmd="mkdir %s/mnt" % testDir, code=0)
    test.runCmdFromRoot(cmd="mkdir %s/mnt/disk_ext" % testDir, code=0)
    test.runCmdFromRoot(cmd="chmod 777 %s/mnt/disk_ext" % testDir, code=0)

    test.mountDev(point="%s/mnt/disk_ext" % testDir, key='-r')

    test.runCmdFromRoot(cmd="touch %s/mnt/disk_ext/test.txt" % testDir, code=1)
    test.runCmdFromRoot(cmd="mkdir %s/mnt/disk_ext/dir" % testDir, code=1)

    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт б')
    test.runCmdFromRoot(cmd="touch %s/imm.txt" % testDir, code=0)
    test.runCmdFromRoot(cmd="chattr +i %s/imm.txt" % testDir, code=0)

    test.runCmdFromRoot(cmd="echo 123 >> %s/imm.txt" % testDir, code=1)
    test.runCmdFromRoot(cmd="rm %s/imm.txt" % testDir, code=1)


    test.runCmdFromRoot(cmd="chattr -i %s/imm.txt" % testDir, code=0)
    test.runCmdFromRoot(cmd="rm %s/imm.txt" % testDir, code=0)


except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()
        test.umountDev(remov=True)

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()



