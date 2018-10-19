#!/usr/bin/python
# coding: utf_8

import os, shutil, pwd, sys, time
from subprocess import check_output
import modules as tm


osf = u'Использование ресурсов'
name = u'Повышенная отказоустойчивость'
osfNum = 8
num = 51
stages = 1
params = ['firstUserName', 'sshHostName', 'sshUserName', 'sshPasswd', 'sshHostName2', 'sshUserName2', 'sshPasswd2']
progress = '2/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

stage = tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
sshHost = test.params['sshHostName']
sshUser = test.params['sshUserName']
sshPasswd = test.params['sshPasswd']

sshHost2 = test.params['sshHostName2']
sshUser2 = test.params['sshUserName2']
sshPasswd2 = test.params['sshPasswd2']

ips = check_output(['hostname', '--all-ip-addresses']).rstrip().split(' ')

ip_virt = '10.81.81.100'

file1 = '/etc/hosts'
file2 = '/tmp/iptables.file'

file3 = '/etc/httpd/conf.d/serverstatus.conf'
file4 = '/etc/httpd/conf/httpd.conf'

file5 = '/var/www/html/index.html'

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()

    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()


    # NODE2--------------------------------------------------------
    test.sshConnect(host=sshHost, user=sshUser, passwd=sshPasswd)

    test.sshActionService('fileprotect', 'stop')

    test.sshCreateCopyFile(file1)
    test.sshRunCmd(cmd='rm -f %s' % file1, code=0)
    test.sshRunCmd(cmd='echo "127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4" >> %s'
                       % file1, code=0)
    test.sshRunCmd(cmd='echo "::1         localhost localhost.localdomain localhost6 localhost6.localdomain6" >> %s'
                       % file1, code=0)
    test.sshRunCmd(cmd='echo "%s node1" >> %s' % (ips[0], file1), code=0)
    test.sshRunCmd(cmd='echo "%s node2" >> %s' % (sshHost, file1), code=0)


    test.sshRunCmd(cmd='iptables-save > %s' % file2, code=0)
    test.sshRunCmd(cmd='iptables -F', code=0)

    test.sshRunCmd(cmd='iptables -I INPUT -m state --state NEW -p udp -m multiport --dports 5404,5405 -j ACCEPT',
                   code=0)
    test.sshRunCmd(cmd='iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 2224 -j ACCEPT', code=0)
    test.sshRunCmd(cmd='iptables -I INPUT -p igmp -j ACCEPT', code=0)
    test.sshRunCmd(cmd='iptables -I INPUT -m addrtype --dst-type MULTICAST -j ACCEPT', code=0)
    test.sshRunCmd(cmd='service iptables save', code=0)

    test.sshInstallPack('corosync')
    test.sshInstallPack('pcs')
    test.sshInstallPack('pacemaker')
    test.sshInstallPack('httpd')

    if test.sshRunCmd('echo -e "qqqwww\nqqqwww\n" | passwd hacluster')['code'] != 0:
        test.addResult(u'Не удалось сменить пароль у пользователя %s:hacluster' % sshHost)

    test.sshRunCmd(cmd='systemctl start pcsd', code=0)

    test.sshDisconnect()








    # NODE1------------------------------------------------------------------------------
    test.createCopyFile(file1)
    test.runCmdFromRoot(cmd='rm -f %s' % file1, code=0)
    test.runCmdFromRoot(cmd='echo "127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4" >> %s'
                       % file1, code=0)
    test.runCmdFromRoot(cmd='echo "::1         localhost localhost.localdomain localhost6 localhost6.localdomain6" >> %s'
                       % file1, code=0)
    test.runCmdFromRoot(cmd='echo "%s node1" >> %s' % (ips[0], file1), code=0)
    test.runCmdFromRoot(cmd='echo "%s node2" >> %s' % (sshHost, file1), code=0)


    test.runCmdFromRoot(cmd='iptables-save > %s' % file2, code=0)
    test.runCmdFromRoot(cmd='iptables -F', code=0)

    test.runCmdFromRoot(cmd='iptables -I INPUT -m state --state NEW -p udp -m multiport --dports 5404,5405 -j ACCEPT',
                   code=0)
    test.runCmdFromRoot(cmd='iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 2224 -j ACCEPT', code=0)
    test.runCmdFromRoot(cmd='iptables -I INPUT -p igmp -j ACCEPT', code=0)
    test.runCmdFromRoot(cmd='iptables -I INPUT -m addrtype --dst-type MULTICAST -j ACCEPT', code=0)
    test.runCmdFromRoot(cmd='service iptables save', code=0)

    test.installPack('corosync')
    test.installPack('pcs')
    test.installPack('pacemaker')
    test.installPack('httpd')

    if test.runCmdFromRoot('echo -e "qqqwww\nqqqwww\n" | passwd hacluster')['code'] != 0:
        test.addResult(u'Не удалось сменить пароль у пользователя hacluster')


    test.runCmdFromRoot(cmd='systemctl start pcsd', code=0)



    test.sshConnect(host=sshHost, user=sshUser, passwd=sshPasswd)
    test.runCmdFromRoot(cmd='pcs cluster destroy --all')
    test.sshRunCmd(cmd='pcs cluster destroy --all')
    test.runCmdFromRoot(cmd='pcs pcsd clear-auth')
    test.sshRunCmd(cmd='pcs pcsd clear-auth')
    test.sshDisconnect()


    test.runCmdFromRoot(cmd='echo -e "hacluster\nqqqwww\n"| pcs cluster auth node1 node2', code=0)

    test.runCmdFromRoot(cmd='pcs cluster setup --name test_cluster node1 node2', code=0)


    test.runCmdFromRoot(cmd='pcs cluster start --all', code=0)
    test.runCmdFromRoot(cmd='pcs status cluster', code=0)
    test.runCmdFromRoot(cmd='pcs property set no-quorum-policy=ignore', code=0)
    test.runCmdFromRoot(cmd='pcs property set stonith-enabled=false', code=0)
    test.runCmdFromRoot(cmd='pcs resource create virtual_ip ocf:heartbeat:IPaddr2 ip=%s cidr_netmask=32 op monitor interval=30s'
                        % ip_virt, code=0)

    status = False
    for i in [1, 2, 3]:
        time.sleep(10)
        res = test.runCmdFromRoot(cmd='pcs status resources', code=0)['output']
        if 'Started node1' in res:
            status = True
            break
    if not status:
        test.addResult(u'Error pcs status resources')















    # ********************************************************************************

    # NODE2
    test.sshConnect(host=sshHost, user=sshUser, passwd=sshPasswd)
    test.sshRunCmd(cmd='iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT', code=0)
    test.sshRunCmd(cmd='service iptables save', code=0)


    test.sshRunCmd(cmd='echo "Listen 127.0.0.1:80" >> %s' % file3)
    test.sshRunCmd(cmd='echo "\t<Location /server-status>" >> %s' % file3)
    test.sshRunCmd(cmd='echo "\tSetHandler server-status" >> %s' % file3)
    test.sshRunCmd(cmd='echo "\tOrder deny,allow" >> %s' % file3)
    test.sshRunCmd(cmd='echo "\tDeny from all" >> %s' % file3)
    test.sshRunCmd(cmd='echo "\tAllow from 127.0.0.1" >> %s' % file3)
    test.sshRunCmd(cmd='echo "</Location>" >> %s' % file3)
    test.showActionMsg('create to file %s: %s' % (sshHost, file3))

    test.sshRunCmd(cmd='echo "<html><h1>node2</h1></html>" >> %s' % file5)
    test.showActionMsg('create to file %s: %s' % (sshHost, file5))

    test.sshCreateCopyFile(file4)
    test.sshRunCmd(cmd="sed -i 's/Listen/#Listen/' %s" % file4, code=0)

    test.sshRunCmd(cmd="systemctl restart httpd", code=0)
    test.sshRunCmd(cmd="wget http://127.0.0.1/server-status", code=0)

    test.sshRunCmd(cmd="systemctl stop httpd", code=0)

    test.sshRunCmd(cmd='echo "Listen %s:80"|sudo tee --append %s' % (ip_virt, file4), code=0)

    test.sshDisconnect()










    # NODE1
    test.runCmdFromRoot(cmd='iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT', code=0)
    test.runCmdFromRoot(cmd='service iptables save', code=0)

    file = open(file3, "w")
    file.write('Listen 127.0.0.1:80\n')
    file.write('<Location /server-status>\n')
    file.write('\tSetHandler server-status\n')
    file.write('\tOrder deny,allow\n')
    file.write('\tDeny from all\n')
    file.write('\tAllow from 127.0.0.1\n')
    file.write('</Location>\n')
    file.close()
    test.showActionMsg('create file %s' % file3)

    file = open(file5, "w")
    file.write('<html><h1>node1</h1></html>\n')
    file.close()
    test.showActionMsg('create file %s' % file5)


    test.createCopyFile(file4)
    test.runCmdFromRoot(cmd="sed -i 's/Listen/#Listen/' %s" % file4, code=0)

    test.runCmdFromRoot(cmd="systemctl restart httpd", code=0)
    test.runCmdFromRoot(cmd="wget http://127.0.0.1/server-status", code=0)

    test.runCmdFromRoot(cmd="systemctl stop httpd", code=0)

    test.runCmdFromRoot(cmd='echo "Listen %s:80"|sudo tee --append %s' % (ip_virt, file4), code=0)








    test.runCmdFromRoot(cmd='pcs resource create webserver ocf:heartbeat:apache configfile=%s statusurl="http://localhost/server-status" op monitor interval=1min'
                            % file4, code=0)
    test.runCmdFromRoot(cmd='pcs constraint colocation add webserver virtual_ip INFINITY', code=0)
    test.runCmdFromRoot(cmd='pcs constraint order virtual_ip then webserver', code=0)
    test.runCmdFromRoot(cmd='pcs constraint location webserver prefers node01=50', code=0)
    test.runCmdFromRoot(cmd='pcs cluster stop --all', code=0)
    test.runCmdFromRoot(cmd='pcs cluster start --all', code=0)



    status = False
    for i in [1, 2, 3]:
        time.sleep(10)
        res = test.runCmdFromRoot(cmd='pcs status | grep virtual_ip', code=0)['output']
        if 'Started node1' in res:
            res = test.runCmdFromRoot(cmd='pcs status | grep webserver', code=0)['output']
            if 'Started node1' in res:
                status = True
                break
    if not status:
        test.addResult(u'Error pcs status')








    # RESULT
    test.sshConnect(host=sshHost2, user=sshUser2, passwd=sshPasswd2)
    res = test.sshRunCmd(cmd='curl http://%s' % ip_virt, code=0)['output']
    if res != '<html><h1>node1</h1></html>':
        test.addResult(u'Ошибка при првверке node1')




    test.runCmdFromRoot(cmd='pcs resource ban webserver', code=0)

    status = False
    for i in [1, 2, 3, 4, 5]:
        time.sleep(10)
        res = test.runCmdFromRoot(cmd='pcs status | grep webserver', code=0)['output']
        if 'Started node2' in res:
            status = True
            break

    if not status:
        test.addResult(u'Error pcs pcs resource ban')


    res = test.sshRunCmd(cmd='curl http://%s' % ip_virt, code=0)['output']
    if res != '<html><h1>node2</h1></html>':
        test.addResult(u'Ошибка при првверке node2')
    test.sshDisconnect()





except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()


        # NODE1
        test.runCmdFromRoot(cmd='iptables-restore %s' % file2, code=0, remov=True)
        test.runCmdFromRoot(cmd='rm %s' % file2, code=0, remov=True)

        test.runCmdFromRoot(cmd='rm %s' % file3, code=0, remov=True)
        test.runCmdFromRoot(cmd='rm %s' % file5, code=0, remov=True)
        test.runCmdFromRoot(cmd='rm %s' % os.path.join(os.getcwd(), 'server-status'), code=0, remov=True)

        test.exchangeCopyFile(file1)
        test.exchangeCopyFile(file4)
        test.uninstallPack('corosync')
        test.uninstallPack('pcs')
        test.uninstallPack('pacemaker')
        test.uninstallPack('httpd')




        # NODE2
        test.sshConnect(host=sshHost, user=sshUser, passwd=sshPasswd)
        test.sshRunCmd(cmd='iptables-restore %s' % file2, code=0, remov=True)
        test.sshRunCmd(cmd='rm %s' % file2, code=0, remov=True)

        test.sshRunCmd(cmd='rm %s' % file3, code=0, remov=True)
        test.sshRunCmd(cmd='rm %s' % file5, code=0, remov=True)

        test.sshExchangeCopyFile(file1)
        test.sshExchangeCopyFile(file4)
        test.sshUninstallPack('corosync')
        test.sshUninstallPack('pcs')
        test.sshUninstallPack('pacemaker')
        test.sshUninstallPack('httpd')

        test.sshCheckService()

        test.sshDisconnect()


    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()



