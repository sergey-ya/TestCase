#!/usr/bin/python
# coding: utf_8


from subprocess import check_output
import os
import modules as tm



osf = u'Защита ОО'
name = u'Конфиденциальность экспортируемых данных ФБО при передаче'
osfNum = 5
num = 35
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

ips = check_output(['hostname', '--all-ip-addresses']).rstrip().split(' ')

file1 = '/etc/pki/rsyslog/ca.pem'
file2 = '/etc/pki/rsyslog/server.pem'
file3 = '/etc/pki/rsyslog/server-key.pem'

file4 = '/etc/pki/rsyslog/ca.pem'
file5 = '/etc/pki/rsyslog/client.pem'
file6 = '/etc/pki/rsyslog/client-key.pem'

file7 = '/etc/rsyslog.d/listen.conf'

file8 = '/etc/rsyslog.d/server-tls.conf'
file9 = '/etc/rsyslog.d/client-tls.conf'

file10 = '/tmp/local.pp'

file11 = '/etc/hosts'

file12 = '/var/log/remote/client.loc/syslog.log'

file13 = os.path.join(os.getcwd(), 'autopass')

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    test.timeStart()

    test.installPack('rsyslog-relp')
    test.installPack('rsyslog-gnutls')
    test.installPack('expect')
    test.runCmdFromRoot(cmd='rm -fr %s' % '/var/log/remote/', code=0)



    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    test.runCmdFromRoot(cmd='cp %s %s' % (os.path.join(os.getcwd(), 'tests/sert/ca.pem'), file1), code=0)
    test.runCmdFromRoot(cmd='cp %s %s' % (os.path.join(os.getcwd(), 'tests/sert/server.pem'), file2), code=0)
    test.runCmdFromRoot(cmd='cp %s %s' % (os.path.join(os.getcwd(), 'tests/sert/server-key.pem'), file3), code=0)

    test.createCopyFile(file7)
    test.runCmdFromRoot(cmd='rm -f %s' % file7, code=0)

    test.createCopyFile(file11)
    test.runCmdFromRoot(cmd='rm -f %s' % file11, code=0)
    test.runCmdFromRoot(cmd='echo "127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4" >> %s'
                            % file11, code=0)
    test.runCmdFromRoot(cmd='echo "::1         localhost localhost.localdomain localhost6 localhost6.localdomain6" >> %s'
                            % file11, code=0)
    test.runCmdFromRoot(cmd='echo "%s client.loc" >> %s' % (sshHost, file11), code=0)

    file = open(file8, "w")
    file.write('module(load="imrelp")\n')
    file.write('input(type="imrelp" port="514" name="tcp-tls"\n')
    file.write('  tls="on"\n')
    file.write('  tls.caCert="%s"\n' % file1)
    file.write('  tls.myCert="%s"\n' % file2)
    file.write('  tls.myPrivKey="%s"\n' % file3)
    file.write('  tls.authMode="name"\n')
    file.write('  tls.permittedpeer=["%s"])\n' % 'client.loc')
    file.write('$template FileForRemote,"/var/log/remote/%fromhost%/syslog.log"\n')
    file.write('if ($inputname contains "tcp-tls") then \n')
    file.write('{\n')
    file.write('  ?FileForRemote\n')
    file.write('  stop\n')
    file.write('}\n')
    file.close()
    test.showActionMsg('create file %s' % file8)

    test.runCmdFromRoot(cmd='systemctl restart rsyslog', code=0)
    test.runCmdFromRoot(cmd='systemctl status rsyslog -l', code=0)







    test.sshConnect(host=sshHost, user=sshUser, passwd=sshPasswd)

    test.sshActionService('fileprotect', 'stop')

    test.sshTimeStart()

    test.sshInstallPack('rsyslog-relp')
    test.sshInstallPack('rsyslog-gnutls')

    test.sshCreateCopyFile(file7)
    test.sshRunCmd(cmd='rm -f %s' % file7, code=0)

    test.sshCreateCopyFile(file11)
    test.sshRunCmd(cmd='rm -f %s' % file11, code=0)
    test.sshRunCmd(cmd='echo "127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4" >> %s'
                       % file11, code=0)
    test.sshRunCmd(cmd='echo "::1         localhost localhost.localdomain localhost6 localhost6.localdomain6" >> %s'
                       % file11, code=0)
    test.sshRunCmd(cmd='echo "%s server.loc" >> %s' % (ips[0], file11), code=0)



    test.sshRunCmd(cmd="echo 'module(load=\"omrelp\")' >> %s" % file9)
    test.sshRunCmd(cmd="echo 'module(load=\"imfile\")' >> %s" % file9)
    test.sshRunCmd(cmd="echo '$template longFormat, \"<%%PRI%%>TIMESTAMP:::date-rfc3339 HOSTNAME syslogtag"
                       "%%msg:::sp-if-no-1st-sp%%%%msg%%\"' >> %s" % file9)
    test.sshRunCmd(cmd="echo '' >> %s" % file9)
    test.sshRunCmd(cmd="echo 'input(type=\"imfile\"' >> %s" % file9)
    test.sshRunCmd(cmd="echo '  file=\"/var/log/audit/audit.log\"' >> %s" % file9)
    test.sshRunCmd(cmd="echo '  tag=\"audiltLogs\"' >> %s" % file9)
    test.sshRunCmd(cmd="echo '  ruleset=\"remotelog\"' >> %s" % file9)
    test.sshRunCmd(cmd="echo ')' >> %s" % file9)
    test.sshRunCmd(cmd="echo 'ruleset(name=\"remotelog\") {' >> %s" % file9)
    test.sshRunCmd(cmd="echo '  action(type=\"omrelp\"' >> %s" % file9)
    test.sshRunCmd(cmd="echo '  target=\"%s\" port=\"514\"' >> %s" % (ips[0], file9))
    test.sshRunCmd(cmd="echo '  tls=\"on\"' >> %s" % file9)
    test.sshRunCmd(cmd="echo '  tls.caCert=\"%s\"' >> %s" % (file4, file9))
    test.sshRunCmd(cmd="echo '  tls.myCert=\"%s\"' >> %s" % (file5, file9))
    test.sshRunCmd(cmd="echo '  tls.myPrivKey=\"%s\"' >> %s" % (file6, file9))
    test.sshRunCmd(cmd="echo '  tls.authmode=\"name\"' >> %s" % file9)
    test.sshRunCmd(cmd="echo '  tls.permittedpeer=[\"%s\"]' >> %s" % ('server.loc', file9))
    test.sshRunCmd(cmd="echo '  template=\"longFormat\")' >> %s" % file9)
    test.sshRunCmd(cmd="echo '}' >> %s" % file9)
    test.showActionMsg('create to file %s: %s' % (sshHost, file9))



    test.runCmdFromRoot(cmd='ssh-keygen -R %s' % sshHost)


    file = open(file13, "w")
    file.write('#!/usr/bin/expect\n')
    file.write('set timeout 2\n')
    file.write('set PASS "%s"\n' % sshPasswd)
    file.write('spawn {*}$argv\n')
    file.write('expect {\n')
    file.write('"(yes/no)?*" {\n')
    file.write('send -- "yes\r"\n')
    file.write('}\n')
    file.write('}\n')
    file.write('expect "assword*"\n')
    file.write('send -- "$PASS\r"\n')
    file.write('interact\n')
    file.close()
    test.showActionMsg('create file %s' % file13)

    test.runCmdFromRoot(cmd='chmod 777 %s' % file13, code=0)



    out = os.path.join(os.getcwd(), 'tests/sert/ca.pem')
    test.runCmdFromRoot(cmd='%s scp %s %s@%s:%s' % (file13, out, sshUser, sshHost, file4), code=0)

    out = os.path.join(os.getcwd(), 'tests/sert/client.pem')
    test.runCmdFromRoot(cmd='%s scp %s %s@%s:%s' % (file13, out, sshUser, sshHost, file5), code=0)

    out = os.path.join(os.getcwd(), 'tests/sert/client-key.pem')
    test.runCmdFromRoot(cmd='%s scp %s %s@%s:%s' % (file13, out, sshUser, sshHost, file6), code=0)

    out = os.path.join(os.getcwd(), 'tests/sert/local.pp')
    test.runCmdFromRoot(cmd='%s scp %s %s@%s:%s' % (file13, out, sshUser, sshHost, file10), code=0)




    test.sshRunCmd(cmd='semodule -i %s' % file10, code=0)
    test.sshRunCmd(cmd='systemctl restart rsyslog', code=0)
    test.sshRunCmd(cmd='systemctl status rsyslog -l', code=0)

    test.sshDisconnect()



    test.runCmdFromRoot(cmd='cat %s' % file12, code=0)



except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.timeEnd()

        test.exchangeCopyFile(file7)
        test.exchangeCopyFile(file11)
        test.runCmdFromRoot(cmd='rm -f %s' % file8, code=0, remov=True)

        test.runCmdFromRoot(cmd='rm -f %s' % file1, code=0, remov=True)
        test.runCmdFromRoot(cmd='rm -f %s' % file2, code=0, remov=True)
        test.runCmdFromRoot(cmd='rm -f %s' % file3, code=0, remov=True)

        test.runCmdFromRoot(cmd='rm -f %s' % file13, code=0, remov=True)

        test.uninstallPack('rsyslog-relp')
        test.uninstallPack('rsyslog-gnutls')
        test.uninstallPack('expect')





        test.sshConnect(host=sshHost, user=sshUser, passwd=sshPasswd)
        test.sshTimeEnd()

        test.sshUninstallPack('rsyslog-relp')
        test.sshUninstallPack('rsyslog-gnutls')

        test.sshExchangeCopyFile(file7)
        test.sshExchangeCopyFile(file11)
        test.sshRunCmd(cmd='rm -f %s' % file9, code=0, remov=True)

        test.sshRunCmd(cmd='rm -f %s' % file4, code=0, remov=True)
        test.sshRunCmd(cmd='rm -f %s' % file5, code=0, remov=True)
        test.sshRunCmd(cmd='rm -f %s' % file6, code=0, remov=True)

        test.sshRunCmd(cmd='rm -f %s' % file10, code=0, remov=True)

        test.sshCheckService()

        test.sshDisconnect()


    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()
