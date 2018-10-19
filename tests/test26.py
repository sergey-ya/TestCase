#!/usr/bin/python
# coding: utf_8

import modules as tm


osf = u'Использование ресурсов'
name = u'Сочетание механизмов аутентификации'
osfNum = 8
num = 26
stages = 1
params = ['firstUserName', 'secondUserName', 'mntDevice']
progress = '2/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
secondUser = test.params['secondUserName']

file1 = '/etc/pam.d/password-auth-ac'
file2 = '/etc/pam.d/system-auth-ac'

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()


    test.installPack('pam_usb')

    test.createCopyFile(file1)
    test.createCopyFile(file2)

    tm.changeRowFile(path=file1, oldRow='auth        required      pam_env.so',
                     newRow='auth        required      pam_usb.so\nauth        required      pam_env.so',
                     start=True)

    tm.changeRowFile(path=file2, oldRow='auth        required      pam_env.so',
                     newRow='auth        required      pam_usb.so\nauth        required      pam_env.so',
                     start=True)


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    test.runCmdFromRoot(cmd="echo 'y' | pamusb-conf --add-device 'Auth-Stick'", code=0)

    if test.runCmdFromRoot(cmd="pamusb-check %s" % firstUser)['code'] != 0:
        test.runCmdFromRoot(cmd="echo 'y' | pamusb-conf --add-user='%s'" % firstUser, code=0)

    if test.runCmdFromRoot(cmd="pamusb-check %s" % secondUser)['code'] == 0:
        test.addResult(msg=u'Необходимо удалить пользователя %s из файла конфигурации ../pamusb.conf')

    res = test.runCmdSecondUser(cmd="echo 'qqqwww' | su %s" % firstUser, code=0)

    res = test.runCmdFirstUser(cmd="echo 'qqqwww' | su %s" % secondUser, code=1)

except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.uninstallPack('pam_usb')

        test.exchangeCopyFile(file1)
        test.exchangeCopyFile(file2)


    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()



