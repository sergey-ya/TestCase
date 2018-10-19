#!/usr/bin/python
# coding: utf_8

import time
from datetime import datetime, timedelta
import string, random
import modules as tm


osf = u'Идентификация и аутентификация'
name = u'Верификация секретов'
osfNum = 3
num = 24
stages = 1
params = ['firstUserName', 'firstUserPass', 'secondUserName']
progress = '2/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
firstUserPass = test.params['firstUserPass']
secondUser = test.params['secondUserName']

file1 = '/etc/pam.d/system-auth-ac'
file2 = '/etc/security/pwquality.conf'

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()


    test.createCopyFile(file1)
    tm.changeRowFile(path=file1, oldRow='password    sufficient',
                     newRow='password    sufficient    pam_unix.so sha512 shadow nullok try_first_pass use_authtok remember=5',
                     start=True)
    test.showActionMsg('change data to file %s' % file1)


    test.createCopyFile(file2)

    tm.changeRowFile(path=file2, oldRow='minlen =', newRow='minlen = 9')
    tm.changeRowFile(path=file2, oldRow='dcredit =', newRow='dcredit = -2')
    tm.changeRowFile(path=file2, oldRow='ucredit =', newRow='ucredit = -3')
    tm.changeRowFile(path=file2, oldRow='lcredit =', newRow='lcredit = -2')
    tm.changeRowFile(path=file2, oldRow='ocredit =', newRow='ocredit = -1')
    test.showActionMsg('change data to file %s' % file2)

    test.runCmdFromRoot(cmd='authconfig --update', code=0)


    test.runCmdFromRoot(cmd='chage -M 90 %s' % firstUser, code=0)
    test.runCmdFromRoot(cmd='chage -W 7 %s' % firstUser, code=0)







    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт а')
    res = test.runCmdFromRoot(cmd='echo -e "Aa\\nAa" | passwd %s' % firstUser, code=0)['error']
    if not u'Пароль является палиндромом' in res:
        test.addResult(msg=u'Ошибка при смене пароля', wait=u'Пароль является палиндромом', taken=res)


    res = test.runCmdFromRoot(cmd='echo -e "Aa12\\nAa12" | passwd %s' % firstUser, code=0)['error']
    if not u'Пароль содержит меньше чем 3 заглавных букв' in res:
        test.addResult(msg=u'Ошибка при смене пароля', wait=u'Пароль содержит меньше чем 3 заглавных букв', taken=res)


    res = test.runCmdFromRoot(cmd='echo -e "Aa12BB\\nAa12BB" | passwd %s' % firstUser, code=0)['error']
    if not u'Пароль содержит меньше чем 2 строчных букв' in res:
        test.addResult(msg=u'Ошибка при смене пароля', wait=u'Пароль содержит меньше чем 2 строчных букв', taken=res)


    res = test.runCmdFromRoot(cmd='echo -e "Aa12BBc\\nAa12BBc" | passwd %s' % firstUser, code=0)['error']
    if not u'Пароль содержит меньше чем 1 не алфавитных символов' in res:
        test.addResult(msg=u'Ошибка при смене пароля', wait=u'Пароль содержит меньше чем 1 не алфавитных символов', taken=res)


    res = test.runCmdFromRoot(cmd='echo -e "Aa12BBc_\\nAa12BBc_" | passwd %s' % firstUser, code=0)['error']
    if not u'В пароле должно быть не меньше 9 символов' in res:
        test.addResult(msg=u'Ошибка при смене пароля', wait=u'В пароле должно быть не меньше 9 символов', taken=res)


    res = test.runCmdFromRoot(cmd='echo -e "Aa12BBc_X\\nAa12BBc_X" | passwd %s' % firstUser, code=0)['error']
    if u'НЕУДАЧНЫЙ ПАРОЛЬ' in res:
        test.addResult(msg=u'Ошибка при смене пароля', wait=u'Not НЕУДАЧНЫЙ ПАРОЛЬ', taken=res)

    res = test.runCmdFromRoot(cmd='echo -e "%s\\n%s" | passwd %s' % (firstUserPass, firstUserPass, firstUser), code=0)





    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт б')

    def changePass(pas1=None, pas2=None, code=None):

        search = None
        if code == 2:
            code = 1
            search = u'Пароль идентичен предыдущему'
            search2 = u'Пароль идентичен предыдущему'
        elif code == 1:
            search = u'Этот пароль уже был использован. Выберите другой.'
            search2 = u'Пароль слишком схож с предыдущим'

        res = test.runCmdFirstUser(cmd='echo -e "%s\\n%s\\n%s" | passwd' % (pas1, pas2, pas2), code=code)

        if search != None:
            if not search in res['error'] and not search2 in res['error']:
                test.addResult(msg=u'Ошибка при смене пароля', wait=search, taken=res['error'])

    def generatePass():
        digit = ''.join(random.choice(string.digits) for _ in range(2))
        upper = ''.join(random.choice(string.ascii_uppercase) for _ in range(3))
        lower = ''.join(random.choice(string.ascii_lowercase) for _ in range(3))
        return digit + upper + lower + '-'

    pass1 = generatePass()
    pass2 = generatePass()
    pass3 = generatePass()
    pass4 = generatePass()
    pass5 = generatePass()
    pass6 = generatePass()
    pass7 = generatePass()

    changePass(pas1=firstUserPass, pas2=pass1, code=0)

    changePass(pas1=pass1, pas2=pass1, code=2)
    changePass(pas1=pass1, pas2=pass2, code=0)

    changePass(pas1=pass2, pas2=pass2, code=2)
    changePass(pas1=pass2, pas2=pass1, code=1)
    changePass(pas1=pass2, pas2=pass3, code=0)

    changePass(pas1=pass3, pas2=pass3, code=2)
    changePass(pas1=pass3, pas2=pass2, code=1)
    changePass(pas1=pass3, pas2=pass1, code=1)
    changePass(pas1=pass3, pas2=pass4, code=0)

    changePass(pas1=pass4, pas2=pass4, code=2)
    changePass(pas1=pass4, pas2=pass3, code=1)
    changePass(pas1=pass4, pas2=pass2, code=1)
    changePass(pas1=pass4, pas2=pass1, code=1)
    changePass(pas1=pass4, pas2=pass5, code=0)

    changePass(pas1=pass5, pas2=pass5, code=2)
    changePass(pas1=pass5, pas2=pass4, code=1)
    changePass(pas1=pass5, pas2=pass3, code=1)
    changePass(pas1=pass5, pas2=pass2, code=1)
    changePass(pas1=pass5, pas2=pass1, code=1)
    changePass(pas1=pass5, pas2=pass6, code=0)

    changePass(pas1=pass6, pas2=pass6, code=2)
    changePass(pas1=pass6, pas2=pass5, code=1)
    changePass(pas1=pass6, pas2=pass4, code=1)
    changePass(pas1=pass6, pas2=pass3, code=1)
    changePass(pas1=pass6, pas2=pass2, code=1)
    changePass(pas1=pass6, pas2=pass1, code=1)
    changePass(pas1=pass6, pas2=pass7, code=0)

    changePass(pas1=pass7, pas2=pass7, code=2)
    changePass(pas1=pass7, pas2=pass6, code=1)
    changePass(pas1=pass7, pas2=pass5, code=1)
    changePass(pas1=pass7, pas2=pass4, code=1)
    changePass(pas1=pass7, pas2=pass3, code=1)
    changePass(pas1=pass7, pas2=pass2, code=1)
    changePass(pas1=pass7, pas2=pass1, code=0)

    test.runCmdFromRoot(cmd='echo -e "%s\\n%s" | passwd %s' % (firstUserPass, firstUserPass, firstUser), code=0)




    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт в')
    now = datetime.today()


    now85 = now + timedelta(days=85)
    test.runCmdFromRoot(cmd='date -s "%s"' % now85.strftime("%b %-d %Y %H:%M:%S"), code=0)
    time.sleep(3)

    res = test.runCmdSecondUser(cmd='echo "%s" | su %s' % (firstUserPass, firstUser), code=0)['output']
    search = u'Предупреждение: срок действия пароля истекает'
    if not search in res:
        test.addResult(msg=u'Ошибка аутентификации', wait=search, taken=res)




    now95 = now + timedelta(days=95)
    test.runCmdFromRoot(cmd='date -s "%s"' % now95.strftime("%b %-d %Y %H:%M:%S"), code=0)
    time.sleep(3)

    res = test.runCmdSecondUser(cmd='echo "%s" | su %s' % (firstUserPass, firstUser), code=1)['error']
    search = u'Пароль: Вам необходимо немедленно сменить пароль (пароль устарел)'
    if not search in res:
        test.addResult(msg=u'Ошибка аутентификации', wait=search, taken=res)



    test.runCmdFromRoot(cmd='date -s "%s"' % now.strftime("%b %-d %Y %H:%M:%S"), code=0, remov=True)





except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.exchangeCopyFile(file1)
        test.exchangeCopyFile(file2)

        test.runCmdFromRoot(cmd='authconfig --update', code=0, remov=True)

        test.runCmdFromRoot(cmd='echo -e "%s\\n%s" | passwd %s' % (firstUserPass, firstUserPass, firstUser), code=0, remov=True)


    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()





