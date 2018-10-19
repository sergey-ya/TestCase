#!/usr/bin/python
# coding: utf_8

import modules as tm


osf = u'Функциональные возможности безопасности операционной системы'
name = u'Блокирование файлов процессами'
osfNum = 7
num = 50
stages = 1
params = ['firstUserName', 'testDir']
progress = '2/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
testDir = test.params['testDir']

file1 = '%s/del_file.txt' % testDir
file2 = '%s/del_file_1.txt' % testDir

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    test.installPack('fileprotect')

    test.runCmdFromRoot(cmd="systemctl start fileprotect", code=0)



    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()


    test.runCmdFirstUser(cmd="touch %s" % file1, code=0)
    test.runCmdFirstUser(cmd="touch %s" % file2, code=0)


    f = open(file1, "r")
    test.runCmdFirstUser(cmd="rm %s" % file1, code=1)
    f.close()

    test.runCmdFirstUser(cmd="rm %s" % file1, code=0)



except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.runCmdFromRoot(cmd="systemctl stop fileprotect", code=0, remov=True)

        test.uninstallPack('fileprotect')

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()



