#!/usr/bin/python
# coding: utf_8


import os, shutil, time
from subprocess import check_output
import modules as tm


osf = u'Защита данных пользователя'
name = u'Установка программного обеспечения'
osfNum = 2
num = 19
stages = 1
params = ['firstUserName', 'sshHostName', 'sshUserName', 'sshPasswd']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
sshHost = test.params['sshHostName']
sshUser = test.params['sshUserName']
sshPasswd = test.params['sshPasswd']


file2 = '/etc/puppet/puppet.conf'

file3 = '/etc/puppet/manifests/site.pp'

file4 = os.path.join(os.getcwd(), 'my-startpuppetma.pp')
file5 = os.path.join(os.getcwd(), 'my-startpuppetma.te')

ips = check_output(['hostname', '--all-ip-addresses']).rstrip().split(' ')

installGedit = None
installFontawesome = None
installGedit2 = None

serv = None
state = None

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()

    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    installGedit = test.runCmdFromRoot(cmd='rpm -qi gedit')['code']
    installFontawesome = test.runCmdFromRoot(cmd='rpm -qi fontawesome-fonts')['code']

    if installFontawesome == 0:
        test.runCmdFromRoot(cmd='yum remove fontawesome-fonts -y', code=0)

    if installGedit == 0:
        test.runCmdFromRoot(cmd='yum remove gedit -y', code=0)


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()
    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт а')
    test.runCmdFirstUser(cmd='rpm -ivh http://mirror.centos.org/centos/7/os/x86_64/Packages/fontawesome-fonts-4.1.0-1.el7.noarch.rpm',
                         code=1)
    test.runCmdFromRoot(cmd='rpm -ivh http://mirror.centos.org/centos/7/os/x86_64/Packages/fontawesome-fonts-4.1.0-1.el7.noarch.rpm',
                        code=0)


    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт б')
    test.runCmdFirstUser(cmd='yum install gedit -y', code=1)
    test.runCmdFromRoot(cmd='yum install gedit -y', code=0)


    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт в')

    test.timeStart()

    test.installPack('puppet-server')


    test.createCopyFile(file2)
    tm.addRowFile(path=file2, oldRow='[main]', newRow='certname = %s\nserver = %s' % (ips[0], ips[0]))
    test.showActionMsg('add data to file %s' % file2)


    test.runCmdFromRoot(cmd="systemctl restart puppetmaster.service", code=0)

    i = 0
    while True:
        test.runCmdFromRoot(cmd="ausearch -c 'start-puppet-ma' | audit2allow -M my-startpuppetma", code=0)
        test.runCmdFromRoot(cmd="semodule -i my-startpuppetma.pp", code=0)

        test.runCmdFromRoot(cmd="rm -rf /var/lib/puppet/ssl", code=0)

        test.runCmdFromRoot(cmd="systemctl restart puppetmaster.service", code=0)

        if test.runCmdFromRoot(cmd="systemctl status puppetmaster.service")['code'] == 0:
            break

        i += 1
        if i == 10:
            test.addResult(msg=u'Не удается добавить политику в SELinux')



    # ЭВМ2************************************************************
    test.sshConnect(host=sshHost, user=sshUser, passwd=sshPasswd)

    test.sshActionService('fileprotect', 'stop')

    test.sshTimeStart()

    test.sshInstallPack('puppet')

    test.sshCreateCopyFile(file2)
    test.sshRunCmd(cmd="sed -i '2iserver = %s' %s" % (ips[0], file2), code=0)
    test.sshRunCmd(cmd="sed -i '2icertname = %s' %s" % (sshHost, file2), code=0)

    test.sshRunCmd(cmd="rm -rf /var/lib/puppet/ssl", code=0)
    time.sleep(3)

    test.sshRunCmd(cmd="systemctl restart puppet", code=0)
    time.sleep(5)
    test.sshDisconnect()
    # ****************************************************************
    #
    # while True:
    #     go = raw_input(" go: ")
    #     if go == 'y':
    #         break


    test.runCmdFromRoot(cmd="puppet cert list", code=0)
    test.runCmdFromRoot(cmd="puppet cert sign %s" % sshHost, code=0)



    file = open(file3, "w")
    file.write('node default {\n')
    file.write('\tpackage { gedit:\n')
    file.write('\t ensure => installed,\n')
    file.write('\t allow_virtual => false,\n')
    file.write('\t}\n')
    file.write('}\n')
    file.close()
    test.showActionMsg('create file %s' % file3)


    # ЭВМ2************************************************************
    test.sshConnect(host=sshHost, user=sshUser, passwd=sshPasswd)

    installGedit2 = test.sshRunCmd(cmd='rpm -qi gedit')['code']
    if installGedit2 == 0:
        test.sshRunCmd(cmd='yum remove gedit -y', code=0)

    test.sshRunCmd(cmd='puppet agent -t', code=2)
    test.sshRunCmd(cmd='rpm -qi gedit', code=0)

    test.sshDisconnect()
    # ****************************************************************




except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        # а-------------------------------------------------------------------------------------------------------------
        if installFontawesome != 0:
            test.runCmdFromRoot(cmd='yum remove fontawesome-fonts -y', code=0, remov=True)
        else:
            test.runCmdFromRoot(cmd='yum install fontawesome-fonts -y', code=0, remov=True)

        # б-------------------------------------------------------------------------------------------------------------
        if installGedit != 0:
            test.runCmdFromRoot(cmd='yum remove gedit -y', code=0, remov=True)
        else:
            test.runCmdFromRoot(cmd='yum install gedit -y', code=0, remov=True)

        # в-------------------------------------------------------------------------------------------------------------
        test.exchangeCopyFile(file2)

        test.runCmdFromRoot(cmd="puppet cert clean %s" % sshHost, code=0, remov=True)
        test.runCmdFromRoot(cmd="puppet cert clean %s" % ips[0], code=0, remov=True)

        test.uninstallPack('puppet-server')

        if test.runCmdFromRoot(cmd='semodule -l | grep my-startpuppetma')['code'] == 0:
            test.runCmdFromRoot(cmd='semodule -r my-startpuppetma', code=0, remov=True)


        test.runCmdFromRoot(cmd='rm %s' % file4, code=0, remov=True)
        test.runCmdFromRoot(cmd='rm %s' % file5, code=0, remov=True)

        test.timeEnd()

        # ЭВМ2************************************************************
        test.sshConnect(host=sshHost, user=sshUser, passwd=sshPasswd)

        if installGedit2 != 0:
            test.sshRunCmd(cmd='yum remove gedit -y', code=0, remov=True)
        else:
            test.sshRunCmd(cmd='yum install gedit -y', code=0, remov=True)

        test.sshTimeEnd()



        test.sshUninstallPack('puppet')

        test.sshExchangeCopyFile(file2)

        test.sshCheckService()

        test.sshDisconnect()
        # ****************************************************************



    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()






