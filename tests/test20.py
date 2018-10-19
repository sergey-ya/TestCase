#!/usr/bin/python
# coding: utf_8

import os, shutil, pwd, sys
import modules as tm


osf = u'Защита данных пользователя'
name = u'Правила контроля запуска компонентов программного обеспечения'
osfNum = 2
num = 20
stages = 2
params = ['firstUserName', 'secondUserName']
progress = '1/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

stage = tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
secondUser = test.params['secondUserName']

file1 = '/etc/systemd/system/test-check.service'
file2 = '/etc/runscr.sh'
file3 = '/home/report.txt'

file4 = '/etc/profile.d/tst.sh'
file5 = '/etc/bashrc'
file6 = '/home/%s/.bashrc' % firstUser


try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock(stage=stage)

    # ПУНКТ В и Д НЕ СДЕЛАН
    # проработать работу с сервисом



    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    service = 'ip6tables.service'

    test.createCopyFile(file5)
    test.createCopyFile(file6)


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    # tm.scanLogFile()

    if stage == 1:
        # --------------------------------------------------------------------------------------------------------------
        tm.showMsg(u'Пункт а')

        if test.runCmdFromRoot(cmd='systemctl status %s' % service)['code'] == 0:
            test.runCmdFromRoot(cmd='systemctl stop %s' % service, code=0)

        test.runCmdFirstUser(cmd='systemctl list-unit-files | grep disabled', code=0)
        test.runCmdFirstUser(cmd='systemctl list-unit-files | grep enabled', code=0)

        test.runCmdFirstUser(cmd='systemctl status %s' % service, code=3)
        test.runCmdFirstUser(cmd='systemctl enable %s' % service, code=1)

        test.runCmdFromRoot(cmd='systemctl enable %s' % service, code=0)
        test.runCmdFromRoot(cmd='systemctl list-unit-files | grep disabled | grep %s' % service, code=1)
        test.runCmdFromRoot(cmd='systemctl list-unit-files | grep enabled | grep %s' % service, code=0)


        # --------------------------------------------------------------------------------------------------------------
        tm.showMsg(u'Пункт б')
        test.runCmdFirstUser(cmd='echo "123" >> %s' % file1, code=1)

        file = open(file1, "w")
        file.write('[Unit]\nDescription=Test Script Service\nAfter=multi-user.target\n')
        file.write('[Service]\nExecStart=%s\n' % file2)
        file.write('[Install]\nWantedBy=default.target\n')
        file.close()
        test.showActionMsg('create file %s' % file1)

        file = open(file2, "w")
        file.write('#!/bin/bash\ndate > %s\n' % file3)
        file.write('du -sh /home/ >> %s\n' % file3)
        file.close()
        test.showActionMsg('create file %s' % file2)

        test.runCmdFromRoot(cmd='chmod 744 %s' % file2, code=0)
        test.runCmdFromRoot(cmd='chmod 664 %s' % file1, code=0)

        test.runCmdFromRoot(cmd='systemctl daemon-reload', code=0)
        test.runCmdFromRoot(cmd='systemctl enable test-check.service', code=0)


        # --------------------------------------------------------------------------------------------------------------
        tm.showMsg(u'Пункт в')

        # test.runCmdFirstUser(cmd='echo "123" >> %s' % file1, code=1)
        #
        #
        # 'vi /etc/xdg/autostart/firefox.desktop'
        #     test.setPause(params=dict(stateService=stateService))

        # --------------------------------------------------------------------------------------------------------------
        tm.showMsg(u'Пункт г')

        test.runCmdFirstUser(cmd='echo "123" >> %s' % file4, code=1)
        test.runCmdFromRoot(cmd='echo "echo \'hello\'" >> %s' % file4, code=0)

        test.runCmdFirstUser(cmd='echo "123" >> %s' % file5, code=1)
        test.runCmdFromRoot(cmd='echo "echo \'user!\'" >> %s' % file5, code=0)

        test.runCmdFirstUser(cmd='echo "echo \'today:\'" >> %s' % file6, code=0)
        test.runCmdFirstUser(cmd='echo "date" >> %s' % file6, code=0)


        res = test.runCmdFirstUser(cmd='id', code=0)['output'].split('\n')
        if res[0] != 'user!':
            test.addResult(msg=u'Некорректный вывод', wait='user!', taken=res[0])
        if res[1] != 'today:':
            test.addResult(msg=u'Некорректный вывод', wait='today:', taken=res[1])

        res = test.runCmdSecondUser(cmd='id', code=0)['output'].split('\n')
        if res[0] != 'user!':
            test.addResult(msg=u'Некорректный вывод', wait='user!', taken=res[1])
        # не хватает проверки на hello


        # --------------------------------------------------------------------------------------------------------------
        tm.showMsg(u'Пункт д')






    if stage == 2:
        # --------------------------------------------------------------------------------------------------------------
        tm.showMsg(u'Пункт а')

        test.runCmdFirstUser(cmd='systemctl list-unit-files | grep enabled | grep %s' % service, code=0)
        test.runCmdFirstUser(cmd='systemctl status %s' % service, code=0)

        test.runCmdFirstUser(cmd='systemctl stop %s' % service, code=1)
        test.runCmdFromRoot(cmd='systemctl stop %s' % service, code=0)

        test.runCmdFirstUser(cmd='systemctl start %s' % service, code=1)
        test.runCmdFromRoot(cmd='systemctl start %s' % service, code=0)

        test.runCmdFirstUser(cmd='systemctl disable %s' % service, code=1)
        test.runCmdFromRoot(cmd='systemctl disable %s' % service, code=0)


        # --------------------------------------------------------------------------------------------------------------
        tm.showMsg(u'Пункт б')

        test.runCmdFirstUser(cmd='ls -la %s' % file3, code=0)
        res = test.runCmdFirstUser(cmd='cat %s' % file3, code=0)['output'].split('\n')
        if res[1].find('M	/home/') == -1:
            test.addResult(msg=u'Некорректное содержание файла %s' % file3)





except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------

        # ПЕРЕБРАТЬ
        rem = False
        if stage == 1:
            test.showEndBlock()

            # г---------------------------------------------------------------------------------------------------------
            test.runCmdFromRoot(cmd='rm %s' % file4, code=0, remov=True)
            test.exchangeCopyFile(file5)
            test.exchangeCopyFile(file6)

            if test.result != [] or test.errorResult != []:
                rem = True
        else:
            rem = True



        if rem:
            test.showEndBlock()

            # а---------------------------------------------------------------------------------------------------------
            # if addParams['stateService'] == 'disabled':
            #     test.runBashFromRoot(cmd='systemctl disable %s' % service, out='')
            # elif addParams['stateService'] == 'enadled':
            #     test.runBashFromRoot(cmd='systemctl enable %s' % service, out='')

            # б---------------------------------------------------------------------------------------------------------
            test.runCmdFromRoot(cmd='systemctl disable test-check.service', code=0, remov=True)
            test.runCmdFromRoot(cmd='systemctl daemon-reload', code=0, remov=True)

            test.runCmdFromRoot(cmd='rm %s' % file1, code=0, remov=True)
            test.runCmdFromRoot(cmd='rm %s' % file2, code=0, remov=True)
            test.runCmdFromRoot(cmd='rm %s' % file3, code=0, remov=True)


    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock(stage=stage)




