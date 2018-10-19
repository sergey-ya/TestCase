#!/usr/bin/python
# coding: utf_8

from modules import runTest
import modules as tm



osf = u'Управление безопасностью'
name = u'Ограниченная по времени авторизация'
osfNum = 4
num = 33
stages = 1
params = ['firstUserName', 'secondUserName']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
secondUser = test.params['secondUserName']

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()

    test.timeStart()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()


    test.runCmdFirstUser(cmd='chage -l %s' % firstUser, code=0)
    test.runCmdFirstUser(cmd='chage -E "2017-11-07" %s' % secondUser, code=1)

    test.sshConnect(host='127.0.0.1', user=secondUser, passwd='qqqwww')
    test.sshDisconnect()
    test.showActionMsg('access to 127.0.0.1 for %s is open' % secondUser)


    test.runCmdFromRoot(cmd='chage -E "2017-11-07" %s' % secondUser, code=0)
    test.runCmdFromRoot(cmd='chage -l %s' % secondUser, code=0)

    try:
        test.sshConnect(host='127.0.0.1', user=secondUser, passwd='qqqwww')
        test.addResult(msg='access to 127.0.0.1 for %s' % secondUser, wait='closed', taken='open')
        test.sshDisconnect()
    except:
        test.showActionMsg('access to 127.0.0.1 for %s is closed' % secondUser)






    test.sshConnect(host='127.0.0.1', user=firstUser, passwd='qqqwww')
    test.sshDisconnect()
    test.showActionMsg('access to 127.0.0.1 for %s is open' % firstUser)

    test.runCmdFirstUser(cmd='chage -M 4 %s' % secondUser, code=1)
    test.runCmdFromRoot(cmd='chage -M 4 %s' % firstUser, code=0)
    test.runCmdFromRoot(cmd='chage -d "2017-11-07" %s' % firstUser, code=0)
    test.runCmdFromRoot(cmd='chage -l %s' % firstUser, code=0)


    test.sshConnect(host='127.0.0.1', user=firstUser, passwd='qqqwww')
    test.sshRunCmd(cmd='id', code=1)
    test.sshDisconnect()

except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.timeEnd()

        test.runCmdFromRoot(cmd='chage -M 99999 %s' % firstUser, code=0, remov=True)
        test.runCmdFromRoot(cmd='chage -d "" %s' % firstUser, code=0, remov=True)

        test.runCmdFromRoot(cmd='chage -d "" %s' % secondUser, code=0, remov=True)
        test.runCmdFromRoot(cmd='chage -E "" %s' % secondUser, code=0, remov=True)

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()


