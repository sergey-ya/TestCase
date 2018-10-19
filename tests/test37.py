#!/usr/bin/python
# coding: utf_8

import os, shutil
import modules as tm



osf = u'Защита ОО'
name = u'Верификация целостности'
osfNum = 5
num = 37
stages = 1
params = ['firstUserName', 'testDir']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
testDir = test.params['testDir']


file1 = "%s/afick_tst.conf" % testDir
file2 = '/home/%s/tst_afick' % firstUser
file3 = '/home/%s/test.txt' % firstUser

dir1 = '/home/%s/af_dir' % firstUser

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    test.installPack('afick')


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    file = open("%s" % file1, "w")
    file.write('database:=%s/afick\n' % testDir)
    file.write('# alias :\n')
    file.write('IV_Home = u+g+p+m+s\n')
    file.write('# files to scan\n')
    file.write('/home/%s IV_Home\n' % firstUser)
    file.close()
    test.showActionMsg('create file %s' % file1)


    test.runCmdFromRoot(cmd='afick -c %s -i' % file1, code=0)
    out1 = test.runCmdFromRoot(cmd='afick -c %s -k' % file1, code=0)['output'].split('\n')


    test.runCmdFirstUser(cmd='touch %s' % file2, code=0)
    test.runCmdFirstUser(cmd='mkdir %s' % dir1, code=0)
    test.runCmdFirstUser(cmd='echo "123" >> %s' % file3, code=0)
    test.runCmdFirstUser(cmd='rmdir %s' % dir1, code=0)


    out2 = test.runCmdFromRoot(cmd='afick -c %s -k' % file1, code=10)['output'].split('\n')

    if len(out2) < len(out1):
        test.addResult(msg=u'Несоответствие вывода afick', wait=out1, taken=out2)


except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.runCmdFromRoot(cmd='rm %s' % file3, code=0, remov=True)
        test.runCmdFromRoot(cmd='rm %s' % file2, code=0, remov=True)

        test.uninstallPack('afick')

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()



