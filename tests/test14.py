#!/usr/bin/python
# coding: utf_8

import time, os
from datetime import datetime
from subprocess import check_output
import modules as tm

osf = u'Защита данных пользователя'
name = u'Фильтрация сетевого потока'
osfNum = 2
num = 14
stages = 1
params = ['firstUserName', 'sshHostName', 'sshUserName', 'sshPasswd']
progress = '0/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
sshHost = test.params['sshHostName']
sshUser = test.params['sshUserName']
sshPass = test.params['sshPasswd']


ips = check_output(['hostname', '--all-ip-addresses']).rstrip().split(' ')

thread = None

time1 = []

file1 = 'pinganalysis.py'
file2 = 'pinglogfile'
file3 = 'iptables.file'


try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()

    # не сделан пункт в г д

    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()


    def clearIPTABLES():
        test.runCmdFromRoot(cmd='iptables -F', code=0)
        res = test.runCmdFromRoot(cmd='iptables -L -n')['output'].split('\n')
        if len(res) != 8:
            test.addResult(msg=u'Ошибка при очистке iptables', wait='no rules', taken=res)


    test.runCmdFromRoot(cmd='iptables-save > %s' % os.path.join(os.getcwd(), file3), code=0)


    test.timeStart()


    test.sshConnect(host=sshHost, user=sshUser, passwd=sshPass)
    test.sshTimeStart()

    now1 = test.runCmdFromRoot(cmd='date +"%b %e %H:%M"', code=0)['output']
    now2 = test.sshRunCmd(cmd='date +"%b %e %H:%M"', code=0)['output']
    test.sshDisconnect()



    if now1 != now2:
        test.addResult(msg=u'Ошибка при сверке времени с удаленной машиной', wait=now1, taken=now2)




    test.sshConnect(host=sshHost, user=sshUser, passwd=sshPass)
    test.sshRunCmd(cmd='echo "#!/usr/bin/python" > %s' % file1)
    test.sshRunCmd(cmd='echo "# coding: utf_8\n" >> %s' % file1)
    test.sshRunCmd(cmd='echo "import time, os" >> %s' % file1)
    test.sshRunCmd(cmd='echo "from datetime import datetime" >> %s' % file1)
    test.sshRunCmd(cmd='echo "from subprocess import Popen, PIPE\n" >> %s' % file1)
    test.sshRunCmd(cmd='echo "def runPing():" >> %s' % file1)
    test.sshRunCmd(cmd='echo "\tproc = Popen(\'sudo -S ping %s -c1\', stdout=PIPE, stderr=PIPE, shell=True)" >> %s' %
                       (ips[0], file1))
    test.sshRunCmd(cmd='echo "\toutput, error = proc.communicate()" >> %s' % file1)
    test.sshRunCmd(cmd='echo "\treturn True if proc.returncode == 0 else False\n" >> %s' % file1)

    test.sshRunCmd(cmd='echo "def writeToLog(data=None):" >> %s' % file1)
    test.sshRunCmd(cmd='echo "\tfile = open(os.path.join(os.getcwd(), \'%s\'), \'a\')" >> %s' % (file2, file1))
    test.sshRunCmd(
        cmd='echo "\tfile.write(datetime.today().strftime(\'%%b %%d %%H:%%M:%%S\') + \'/\' + str(data) + \'\\n\')" >> %s' % file1)
    test.sshRunCmd(cmd='echo "\tfile.close()\n" >> %s' % file1)

    test.sshRunCmd(cmd='echo "file = open(os.path.join(os.getcwd(), \'%s\'), \'w\')" >> %s' % (file2, file1))
    test.sshRunCmd(cmd='echo "file.close()\n" >> %s' % file1)
    test.sshRunCmd(cmd='echo "res1 = \'\'" >> %s' % file1)
    test.sshRunCmd(cmd='echo "count = 0" >> %s' % file1)
    test.sshRunCmd(cmd='echo "while True:" >> %s' % file1)
    test.sshRunCmd(cmd='echo "\tres2 = runPing()" >> %s' % file1)
    test.sshRunCmd(cmd='echo "\tif res1 != res2:" >> %s' % file1)
    test.sshRunCmd(cmd='echo "\t\tres1 = res2" >> %s' % file1)
    test.sshRunCmd(cmd='echo "\t\twriteToLog(res2)" >> %s' % file1)
    test.sshRunCmd(cmd='echo "\tcount += 1" >> %s' % file1)
    test.sshRunCmd(cmd='echo "\ttime.sleep(1)" >> %s' % file1)
    test.sshRunCmd(cmd='echo "\tif count == 55:" >> %s' % file1)
    test.sshRunCmd(cmd='echo "\t\tbreak" >> %s' % file1)
    test.showActionMsg('create to file %s: %s' % (sshHost, file1))
    test.sshRunCmd(cmd='chmod 777 %s' % file1, code=0)
    test.sshDisconnect()




    test.runCmdFromRoot(cmd='systemctl restart iptables', code=0)
    clearIPTABLES()
    # test.installPack('nc')









    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    def analysis(data1=None, data2=None):
        res1 = []
        res2 = []
        for i in data2:
            k = i.split('/')
            res1.append(k[0])
            res2.append(k[1])

        if res1[0] < data1[0] and data1[0] < res1[1] < data1[1] and data1[1] < res1[2] < data1[2] and \
                data1[2] < res1[3] < data1[3] and data1[3] < res1[4]:
            if res2[0] == 'True' and res2[1] == 'False' and res2[2] == 'True' and res2[3] == 'False' \
                    and res2[4] == 'True':
                pass
            else:
                test.addResult(msg=u'Ошибка при проверки состояний соединения на удаленной машине',
                               wait='True, False, True, False, True', taken=res2)
        else:
            test.addResult(msg=u'Ошибка при сверке тайминга соединения на удаленной машине',
                           wait=data1, taken=res1)

        dat = data1[4]
        if dat[4] == '0':
            dat = dat[0:4] + ' ' + dat[5:]
        test.runCmdFromRoot(cmd='cat /var/log/messages | grep "%s.*SRC=%s DST=%s"' % (dat, sshHost, ips[0]), code=0)



    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт а')

    test.runCmdFromRoot(cmd='ping %s -c1' % sshHost, code=0)


    thread = tm.MyThread2(host=sshHost, user=sshUser, passwd=sshPass, cmd='nohup ./%s &' % file1)
    thread.start()



    time.sleep(10)
    time1.append(datetime.today().strftime("%b %d %H:%M:%S"))

    test.runCmdFromRoot(cmd='iptables -A INPUT -s %s -j DROP' % sshHost, code=0)
    test.runCmdFromRoot(cmd='iptables -L INPUT | grep "DROP.*all.*--.*%s.*anywhere"' % sshHost, code=0)


    err = test.runCmdFromRoot(cmd='ping %s -c1' % sshHost, code=1)['error']
    if err != '':
        test.addResult(msg=u'Не верный ответ на команду ping', wait=u'null', taken=err)


    time.sleep(10)
    clearIPTABLES()
    time1.append(datetime.today().strftime("%b %d %H:%M:%S"))





    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт б')

    time.sleep(10)
    time1.append(datetime.today().strftime("%b %d %H:%M:%S"))

    test.runCmdFromRoot(cmd='iptables -A OUTPUT -d %s -j DROP' % sshHost, code=0)
    test.runCmdFromRoot(cmd='iptables -L OUTPUT | grep "DROP.*all.*--.*anywhere.*%s"' % sshHost, code=0)


    err = test.runCmdFromRoot(cmd='ping %s -c1' % sshHost, code=1)['error']
    if err != u'ping: sendmsg: Операция не позволена':
        test.addResult(msg=u'Не верный ответ на команду ping', wait=u'ping: sendmsg: Операция не позволена', taken=err)


    time.sleep(10)
    clearIPTABLES()
    time1.append(datetime.today().strftime("%b %d %H:%M:%S"))



    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт д')








    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт e')

    time.sleep(10)
    test.runCmdFromRoot(cmd='iptables -A INPUT -p ICMP --icmp-type 8 -j LOG --log-prefix "Iptables: Ping detected: "', code=0)
    test.runCmdFromRoot(cmd='iptables -A INPUT -p ICMP --icmp-type 8 -j ACCEPT', code=0)
    test.runCmdFromRoot(cmd='iptables -L INPUT | grep "LOG.*icmp.*--.*anywhere.*anywhere.*icmp echo-request LOG level warning prefix"', code=0)
    test.runCmdFromRoot(cmd='iptables -L INPUT | grep "ACCEPT.*icmp.*--.*anywhere.*anywhere.*icmp echo-request"', code=0)

    time.sleep(5)
    time1.append(datetime.today().strftime("%b %d %H:%M:%S"))
    time.sleep(5)




    # ------------------------------------------------------------------------------------------------------------------
    thread.join()

    test.sshConnect(host=sshHost, user=sshUser, passwd=sshPass)
    time2 = test.sshRunCmd(cmd='cat %s' % file2, code=0)['output'].split('\n')
    test.sshDisconnect()

    analysis(data1=time1, data2=time2)



except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.runCmdFromRoot(cmd='iptables-restore %s' % os.path.join(os.getcwd(), file3), code=0, remov=True)
        test.runCmdFromRoot(cmd='rm %s' % file3, code=0, remov=True)

        test.timeEnd()

        # test.uninstallPack('nc')

        test.sshConnect(host=sshHost, user=sshUser, passwd=sshPass)
        test.sshTimeEnd()

        test.sshRunCmd(cmd='rm -f %s' % file2, code=0, remov=True)
        test.sshRunCmd(cmd='rm -f %s' % file1, code=0, remov=True)
        test.sshDisconnect()

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()

