#!/usr/bin/python
# coding: utf_8

import modules as tm



osf = u'Идентификация и аутентификация'
name = u'Обработка отказов аутентификации'
osfNum = 3
num = 22
stages = 1
params = ['firstUserName', 'secondUserName']
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



    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    def checkAuth(pas=None, code=None):

        search = None

        if code == 2:
            code = 1
            search = u'Доступ запрещен'
        elif code == 1:
            search = u'Сбой при проверке подлинности'

        res = test.runCmdFirstUser(cmd='echo "%s" | su %s' % (pas, secondUser), code=code)

        if search != None:
            if not search in res['error']:
                test.addResult(msg=u'Ошибка при проверке аутентификации', wait=search, taken=res['error'])


    checkAuth(pas='qqqwww123', code=1)
    checkAuth(pas='qqqwww123', code=1)
    checkAuth(pas='qqqwww', code=0)


    test.createCopyFile(file1)
    tm.changeRowFile(path=file1, oldRow='auth        required      pam_env.so',
                     newRow='auth        required      pam_env.so\nauth        required      pam_faillock.so preauth silent audit deny=2 unlock_time=300',
                     start=True)
    tm.changeRowFile(path=file1, oldRow='auth        sufficient    pam_unix.so nullok try_first_pass',
                     newRow='auth        sufficient    pam_unix.so nullok try_first_pass\n'
                            'auth        [default=die] pam_faillock.so authfail audit deny=2 unlock_time=300',
                     start=True)
    tm.changeRowFile(path=file1, oldRow='account     required      pam_permit.so',
                     newRow='account     required      pam_permit.so\naccount     required      pam_faillock.so',
                     start=True)


    test.createCopyFile(file2)
    tm.changeRowFile(path=file2, oldRow='auth        required      pam_env.so',
                     newRow='auth        required      pam_env.so\nauth        required      pam_faillock.so preauth silent audit deny=2 unlock_time=300',
                     start=True)
    tm.changeRowFile(path=file2, oldRow='auth        sufficient    pam_unix.so nullok try_first_pass',
                     newRow='auth        sufficient    pam_unix.so nullok try_first_pass\n'
                            'auth        [default=die] pam_faillock.so authfail audit deny=2 unlock_time=300',
                     start=True)
    tm.changeRowFile(path=file2, oldRow='account     required      pam_permit.so',
                     newRow='account     required      pam_permit.so\naccount     required      pam_faillock.so',
                     start=True)


    checkAuth(pas='qqqwww123', code=2)
    checkAuth(pas='qqqwww123', code=2)
    checkAuth(pas='qqqwww', code=1)

    test.runCmdFromRoot(cmd='faillock --user %s --reset' % secondUser, code=0)

    checkAuth(pas='qqqwww', code=0)




except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.exchangeCopyFile(file1)
        test.exchangeCopyFile(file2)

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()