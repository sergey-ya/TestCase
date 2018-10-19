#!/usr/bin/python
# coding: utf_8


from datetime import datetime
import time
from subprocess import check_output
import modules as tm


osf = u'Доступ к ОО'
name = u'Открытие сеанса с ОО'
osfNum = 6
num = 49
stages = 1
params = ['firstUserName', 'secondUserName', 'sshHostName', 'sshUserName', 'sshPasswd']
progress = '2/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
secondUser = test.params['secondUserName']
sshHost = test.params['sshHostName']
sshUser = test.params['sshUserName']
sshPasswd = test.params['sshPasswd']

file1 = '/etc/security/time.conf'
file2 = '/etc/pam.d/password-auth-ac'
file3 = '/etc/pam.d/system-auth-ac'
file4 = 'sshanalysis.py'
file5 = 'sshlogfile'
file6 = '/etc/hosts.deny'

currentNow = None

ips = check_output(['hostname', '--all-ip-addresses']).rstrip().split(' ')

time1 = []


try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()

    # ПУНКТ В - доделать последнюю проверку
    # ПУНКТ Г - НЕ ВЫПОЛНИМ (TTY)

    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    test.timeStart()


    test.sshConnect(host=sshHost, user=sshUser, passwd=sshPasswd)
    test.sshTimeStart()



    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт а')

    test.runCmdFirstUser(cmd="echo 'qqqwww' | su %s" % secondUser, code=0)

    test.runCmdFromRoot(cmd="passwd -l %s" % secondUser, code=0)
    test.runCmdFirstUser(cmd="echo 'qqqwww' | su %s" % secondUser, code=1)

    test.runCmdFromRoot(cmd="passwd -u %s" % secondUser, code=0)
    test.runCmdFirstUser(cmd="echo 'qqqwww' | su %s" % secondUser, code=0)


    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт б')

    def analysis(data1=None, data2=None):
        res1 = []
        res2 = []
        for i in data2:
            k = i.split('/')
            res1.append(k[0])
            res2.append(k[1])

        if data1[0] < res1[0] < data1[1] and data1[1] < res1[1] < data1[2] and data1[2] < res1[2] < data1[3]:
            if res2[0] == 'True' and res2[1] == 'False' and res2[2] == 'True':
                pass
            else:
                test.addResult(msg=u'Ошибка при проверки состояний соединения на удаленной машине',
                               wait='True, False, True', taken=res2)
        else:
            test.addResult(msg=u'Ошибка при сверке тайминга соединения на удаленной машине',
                           wait=data1, taken=res1)


    test.sshRunCmd(cmd='echo "#!/usr/bin/python" > %s' % file4)
    test.sshRunCmd(cmd='echo "# coding: utf_8\n" >> %s' % file4)
    test.sshRunCmd(cmd='echo "import time, os" >> %s' % file4)
    test.sshRunCmd(cmd='echo "from datetime import datetime" >> %s' % file4)
    test.sshRunCmd(cmd='echo "from subprocess import Popen, PIPE\n" >> %s' % file4)

    test.sshRunCmd(cmd='echo "def runSSHConnect():" >> %s' % file4)
    test.sshRunCmd(cmd='echo "\tproc = Popen(\'ssh -o PreferredAuthentications=none %s\', stdout=PIPE, stderr=PIPE, shell=True)" >> %s' %
                       (ips[0], file4))
    test.sshRunCmd(cmd='echo "\toutput, error = proc.communicate()" >> %s' % file4)
    test.sshRunCmd(cmd='echo "\treturn False if \'ssh_exchange_identification: read: Connection reset by peer\' in error else True\n" >> %s' % file4)

    test.sshRunCmd(cmd='echo "def writeToLog(data=None):" >> %s' % file4)
    test.sshRunCmd(cmd='echo "\tfile = open(os.path.join(os.getcwd(), \'%s\'), \'a\')" >> %s' % (file5, file4))
    test.sshRunCmd(
        cmd='echo "\tfile.write(datetime.today().strftime(\'%%b %%-d %%H:%%M:%%S\') + \'/\' + str(data) + \'\\n\')" >> %s' % file4)
    test.sshRunCmd(cmd='echo "\tfile.close()\n" >> %s' % file4)

    test.sshRunCmd(cmd='echo "file = open(os.path.join(os.getcwd(), \'%s\'), \'w\')" >> %s' % (file5, file4))
    test.sshRunCmd(cmd='echo "file.close()\n" >> %s' % file4)
    test.sshRunCmd(cmd='echo "res1 = \'\'" >> %s' % file4)
    test.sshRunCmd(cmd='echo "count = 0" >> %s' % file4)
    test.sshRunCmd(cmd='echo "while True:" >> %s' % file4)
    test.sshRunCmd(cmd='echo "\tres2 = runSSHConnect()" >> %s' % file4)
    test.sshRunCmd(cmd='echo "\tif res1 != res2:" >> %s' % file4)
    test.sshRunCmd(cmd='echo "\t\tres1 = res2" >> %s' % file4)
    test.sshRunCmd(cmd='echo "\t\twriteToLog(res2)" >> %s' % file4)
    test.sshRunCmd(cmd='echo "\tcount += 1" >> %s' % file4)
    test.sshRunCmd(cmd='echo "\ttime.sleep(1)" >> %s' % file4)
    test.sshRunCmd(cmd='echo "\tif count == 15:" >> %s' % file4)
    test.sshRunCmd(cmd='echo "\t\tbreak" >> %s' % file4)
    test.showActionMsg('create to file %s: %s' % (sshHost, file4))

    test.sshRunCmd(cmd='chmod 777 %s' % file4, code=0)


    test.createCopyFile(file6)


    time1.append(datetime.today().strftime("%b %-d %H:%M:%S"))
    time.sleep(2)
    thread = tm.MyThread2(host=sshHost, user=sshUser, passwd=sshPasswd, cmd='nohup ./%s &' % file4)
    thread.start()
    time.sleep(10)
    time1.append(datetime.today().strftime("%b %-d %H:%M:%S"))

    test.runCmdFromRoot(cmd='echo "ALL:%s" >> %s' % (sshHost, file6), code=0)
    time.sleep(10)
    time1.append(datetime.today().strftime("%b %-d %H:%M:%S"))


    test.runCmdFromRoot(cmd="sed -i '/%s/d' %s" % (sshHost, file6), code=0)
    time.sleep(10)
    time1.append(datetime.today().strftime("%b %-d %H:%M:%S"))


    thread.join()

    time2 = test.sshRunCmd(cmd='cat %s' % file5, code=0)['output'].split('\n')
    test.sshDisconnect()

    analysis(data1=time1, data2=time2)


    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт в')

    test.createCopyFile(file1)
    test.runCmdFromRoot(cmd="echo 'login | gdm-password ; * ; * ; !Wd0000-2400' >> %s" % file1, code=0)

    test.createCopyFile(file2)
    test.createCopyFile(file3)

    tm.changeRowFile(path=file2, oldRow='account     required      pam_unix.so',
                     newRow='account     required      pam_time.so\naccount     required      pam_unix.so',
                     start=True)

    tm.changeRowFile(path=file3, oldRow='account     required      pam_unix.so',
                     newRow='account     required      pam_time.so\naccount     required      pam_unix.so',
                     start=True)


    currentNow = datetime.strftime(datetime.now(), "%Y-%m-%d")

    test.runCmdFromRoot(cmd='date +%Y%m%d -s "20180926"', code=0)


    time.sleep(2)
    test.runCmdFirstUser(cmd="echo 'qqqwww' | su %s" % secondUser, code=0)
    test.runCmdSecondUser(cmd="echo 'qqqwww' | su %s" % firstUser, code=0)


    test.runCmdFromRoot(cmd='date +%Y%m%d -s "20180922"', code=0)
    time.sleep(2)


    # test.runCmdFirstUser(cmd="echo 'qqqwww' | su %s" % secondUser, code=1)
    # test.runCmdSecondUser(cmd="echo 'qqqwww' | su %s" % firstUser, code=1)


except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.exchangeCopyFile(file1)
        test.exchangeCopyFile(file2)
        test.exchangeCopyFile(file3)
        test.exchangeCopyFile(file6)


        test.runCmdFromRoot(cmd='date -s %s' % currentNow, code=0, remov=True)

        test.timeEnd()



        test.sshConnect(host=sshHost, user=sshUser, passwd=sshPasswd)

        test.sshTimeEnd()

        test.sshRunCmd(cmd='rm -f %s' % file4, code=0, remov=True)
        test.sshRunCmd(cmd='rm -f %s' % file5, code=0, remov=True)
        test.sshDisconnect()


    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()



