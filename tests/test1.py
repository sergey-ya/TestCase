#!/usr/bin/python
# coding: utf_8


from datetime import datetime, timedelta
import time
import socket
import modules as tm


osf = u'Аудит'
name = u'Сигналы нарушения безопасности'
osfNum = 1
num = 1
stages = 1
params = ['firstUserName']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']


file1 = '/etc/sudoers'
file2 = '/var/spool/mail/root'

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    test.createCopyFile(file1)

    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    text = []
    text.append('Defaults mailto="root@%s"' % socket.gethostname())
    text.append('Defaults mail_badpass')
    text.append('Defaults mail_no_perms')
    text.append('Defaults mail_no_user')
    text.append('Defaults mail_always')
    tm.addRowToFile(file=file1, text=text)
    test.showActionMsg('add data to file %s' % file1)

    test.runCmdFirstUser(cmd='sudo su', code=1)
    time.sleep(3)


    today = datetime.today()

    findText1 = socket.gethostname() + ' : ' + today.strftime("%b %d ").replace(' 0', '  ')
    findText1 = findText1 + today.strftime("%H:")
    findText2 = '%s : user NOT in sudoers' % firstUser
    findText3 = 'COMMAND=/bin/su'


    if test.runCmdFromRoot(cmd='cat %s | grep "%s.*%s.*%s"' %
                               (file2, findText1, findText2, findText3))['code'] != 0:
        test.addResult(msg=u'Не найдено извещение о нарушении информационной безопасности.',
                       wait='param1:%s, param2:%s, param3:%s' % (findText1, findText2, findText3),
                       taken='file /var/spool/mail/root')



except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()
        test.exchangeCopyFile(file1)


    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()
