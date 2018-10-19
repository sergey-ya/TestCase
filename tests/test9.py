#!/usr/bin/python
# coding: utf_8

import os, shutil
import modules as tm



osf = u'Защита данных пользователя'
name = u'Дискреционное управление доступом — общий механизм'
osfNum = 2
num = 9
stages = 1
params = ['firstUserName', 'secondUserName', 'testDir']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
secondUser = test.params['secondUserName']
testDir = test.params['testDir']

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    test.runCmdFromRoot(cmd="mkdir %s/dir_wr" % testDir, code=0)
    test.runCmdFromRoot(cmd="chmod 330 %s/dir_wr/" % testDir, code=0)
    test.runCmdFromRoot(cmd="mkdir %s/dir_read" % testDir, code=0)
    test.runCmdFromRoot(cmd="chmod 440 %s/dir_read/" % testDir, code=0)
    test.runCmdFromRoot(cmd="mkdir %s/dir_wr_read" % testDir, code=0)
    test.runCmdFromRoot(cmd="chmod 660 %s/dir_wr_read/" % testDir, code=0)
    test.runCmdFromRoot(cmd="mkdir %s/dir_exec" % testDir, code=0)
    test.runCmdFromRoot(cmd="chmod 110 %s/dir_exec/" % testDir, code=0)
    test.runCmdFromRoot(cmd="mkdir %s/tst_fldr/" % testDir, code=0)
    test.runCmdFromRoot(cmd="touch %s/tst_fldr/read_only.txt" % testDir, code=0)
    test.runCmdFromRoot(cmd="chmod 440 %s/tst_fldr/read_only.txt" % testDir, code=0)
    test.runCmdFromRoot(cmd="touch %s/tst_fldr/rw.txt" % testDir, code=0)
    test.runCmdFromRoot(cmd="chmod 660 %s/tst_fldr/rw.txt" % testDir, code=0)
    test.runCmdFromRoot(cmd="touch %s/tst_fldr/write_only.txt" % testDir, code=0)
    test.runCmdFromRoot(cmd="chmod 220 %s/tst_fldr/write_only.txt" % testDir, code=0)
    test.runCmdFromRoot(cmd="touch %s/tst_fldr/exec_only.sh" % testDir, code=0)
    test.runCmdFromRoot(cmd="chmod 550 %s/tst_fldr/exec_only.sh" % testDir, code=0)


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    def runAnalis(r1=1, r2=1, r3=1, r4=1, w1=1, w2=1, w3=1, w4=1, e1=126, e2=126, e3=126, e4=126, u_name=None):
        # read
        test.runCmdFromUser(user=u_name, cmd="cat %s/tst_fldr/read_only.txt" % testDir, code=r1)
        test.runCmdFromUser(user=u_name, cmd="cat %s/tst_fldr/rw.txt" % testDir, code=r2)
        test.runCmdFromUser(user=u_name, cmd="cat %s/tst_fldr/write_only.txt" % testDir, code=r3)
        test.runCmdFromUser(user=u_name, cmd="cat %s/tst_fldr/exec_only.sh" % testDir, code=r4)

        # write
        test.runCmdFromUser(user=u_name, cmd="echo 'txt' > %s/tst_fldr/read_only.txt" % testDir, code=w1)
        test.runCmdFromUser(user=u_name, cmd="echo 'txt' > %s/tst_fldr/rw.txt" % testDir, code=w2)
        test.runCmdFromUser(user=u_name, cmd="echo 'txt' > %s/tst_fldr/write_only.txt" % testDir, code=w3)
        test.runCmdFromUser(user=u_name, cmd="echo 'txt' > %s/tst_fldr/exec_only.sh" % testDir, code=w4)

        # execute
        test.runCmdFromUser(user=u_name, cmd="%s/tst_fldr/read_only.txt" % testDir, code=e1)
        test.runCmdFromUser(user=u_name, cmd="%s/tst_fldr/rw.txt" % testDir, code=e2)
        test.runCmdFromUser(user=u_name, cmd="%s/tst_fldr/write_only.txt" % testDir, code=e3)
        test.runCmdFromUser(user=u_name, cmd="%s/tst_fldr/exec_only.sh" % testDir, code=e4)

    def runAnalis2(r1=2, r2=2, r3=2, r4=2, w1=1, w2=1, w3=1, w4=1, c1=1, c2=1, c3=1, c4=1, u_name=None):
        # read
        test.runCmdFromUser(user=u_name, cmd="ls -l %s/dir_read/" % testDir, code=r1)
        test.runCmdFromUser(user=u_name, cmd="ls -l %s/dir_wr_read/" % testDir, code=r2)
        test.runCmdFromUser(user=u_name, cmd="ls -l %s/dir_wr/" % testDir, code=r3)
        test.runCmdFromUser(user=u_name, cmd="ls -l %s/dir_exec/" % testDir, code=r4)

        # write
        test.runCmdFromUser(user=u_name, cmd="touch %s/dir_read/test.txt" % testDir, code=w1)
        test.runCmdFromUser(user=u_name, cmd="touch %s/dir_wr_read/test.txt" % testDir, code=w2)
        test.runCmdFromUser(user=u_name, cmd="touch %s/dir_wr/test.txt" % testDir, code=w3)
        test.runCmdFromUser(user=u_name, cmd="touch %s/dir_exec/test.txt" % testDir, code=w4)

        # cd
        test.runCmdFromUser(user=u_name, cmd="cd %s/dir_read/" % testDir, code=c1)
        test.runCmdFromUser(user=u_name, cmd="cd %s/dir_wr_read/" % testDir, code=c2)
        test.runCmdFromUser(user=u_name, cmd="cd %s/dir_wr/" % testDir, code=c3)
        test.runCmdFromUser(user=u_name, cmd="cd %s/dir_exec/" % testDir, code=c4)

        # удаляем данные из каталогов
        file1 = "%s/dir_read/test.txt" % testDir
        file2 = "%s/dir_wr_read/test.txt" % testDir
        file3 = "%s/dir_wr/test.txt" % testDir
        file4 = "%s/dir_exec/test.txt" % testDir
        if os.path.isfile(file1):
            os.remove(file1)
        if os.path.isfile(file2):
            os.remove(file2)
        if os.path.isfile(file3):
            os.remove(file3)
        if os.path.isfile(file4):
            os.remove(file4)

    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт а')
    runAnalis(u_name=firstUser)
    runAnalis(u_name=secondUser)

    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт б')
    test.runCmdFromRoot(cmd="chown -R %s %s/tst_fldr/" % (firstUser, testDir), code=0)
    runAnalis(u_name=firstUser, r1=0, r2=0, r4=0, w2=0, w3=0, e4=0)
    runAnalis(u_name=secondUser)

    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт в')
    test.runCmdFromRoot(cmd="chown -R root:%s %s/tst_fldr/" % (firstUser, testDir), code=0)
    runAnalis(u_name=firstUser, r1=0, r2=0, r4=0, w2=0, w3=0, e4=0)
    runAnalis(u_name=secondUser)

    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт г')
    test.runCmdFromRoot(cmd="usermod -a -G audio %s" % firstUser, code=0)
    test.runCmdFromRoot(cmd="usermod -a -G audio %s" % secondUser, code=0)
    test.runCmdFromRoot(cmd="chown -R root:audio %s/tst_fldr/" % testDir, code=0)
    runAnalis(u_name=firstUser, r1=0, r2=0, r4=0, w2=0, w3=0, e4=0)
    runAnalis(u_name=secondUser, r1=0, r2=0, r4=0, w2=0, w3=0, e4=0)

    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт д')
    runAnalis2(u_name=firstUser)
    runAnalis2(u_name=secondUser)

    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт е')
    test.runCmdFromRoot(cmd="chown %s %s/dir_read/" % (firstUser, testDir), code=0)
    test.runCmdFromRoot(cmd="chown %s %s/dir_wr_read/" % (firstUser, testDir), code=0)
    test.runCmdFromRoot(cmd="chown %s %s/dir_wr/" % (firstUser, testDir), code=0)
    test.runCmdFromRoot(cmd="chown %s %s/dir_exec/" % (firstUser, testDir), code=0)
    runAnalis2(u_name=firstUser, r1=0, r2=0, w3=0, c3=0, c4=0)
    runAnalis2(u_name=secondUser)

    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт ж')
    test.runCmdFromRoot(cmd="chown root:%s %s/dir_read/" % (firstUser, testDir), code=0)
    test.runCmdFromRoot(cmd="chown root:%s %s/dir_wr_read/" % (firstUser, testDir), code=0)
    test.runCmdFromRoot(cmd="chown root:%s %s/dir_wr/" % (firstUser, testDir), code=0)
    test.runCmdFromRoot(cmd="chown root:%s %s/dir_exec/" % (firstUser, testDir), code=0)
    runAnalis2(u_name=firstUser, r1=0, r2=0, w3=0, c3=0, c4=0)
    runAnalis2(u_name=secondUser)

    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт з')
    test.runCmdFromRoot(cmd="chown root:audio %s/dir_read/" % testDir, code=0)
    test.runCmdFromRoot(cmd="chown root:audio %s/dir_wr_read/" % testDir, code=0)
    test.runCmdFromRoot(cmd="chown root:audio %s/dir_wr/" % testDir, code=0)
    test.runCmdFromRoot(cmd="chown root:audio %s/dir_exec/" % testDir, code=0)
    runAnalis2(u_name=firstUser, r1=0, r2=0, w3=0, c3=0, c4=0)
    runAnalis2(u_name=secondUser, r1=0, r2=0, w3=0, c3=0, c4=0)

    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт и')
    test.runCmdFromRoot(cmd="chmod 777 %s" % testDir, code=0)
    test.runCmdFromRoot(cmd="chmod o+t %s" % testDir, code=0)
    test.runCmdFromUser(user=firstUser, cmd="touch %s/ivanov.file" % testDir, code=0)
    test.runCmdFromUser(user=firstUser, cmd="chmod 1777 %s/ivanov.file" % testDir, code=0)
    test.runCmdFromRoot(cmd="chown %s:audio %s/ivanov.file" % (firstUser, testDir), code=0)
    test.runCmdFromUser(user=secondUser, cmd="rm %s/ivanov.file" % testDir, code=1)
    test.runCmdFromUser(user=firstUser, cmd="rm %s/ivanov.file" % testDir, code=0)


except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.runCmdFromRoot(cmd="gpasswd -d %s audio" % firstUser, code=0, remov=True)
        test.runCmdFromRoot(cmd="gpasswd -d %s audio" % secondUser, code=0, remov=True)
    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()

