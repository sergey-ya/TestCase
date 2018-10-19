#!/usr/bin/python
# coding: utf_8

import os, shutil, pwd
import time
import modules as tm


osf = u'Защита данных пользователя'
name = u'Ролевое управление доступом'
osfNum = 2
num = 12
stages = 1
params = ['firstUserName', 'firstUserPass', 'testDir']
progress = '2/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
firstUserPass = test.params['firstUserPass']
testDir = test.params['testDir']

file1 = '%s/systemd_webadm.te' % testDir
file2 = '%s/systemd_webadm.mod' % testDir
file3 = '%s/systemd_webadm.pp' % testDir
file4 = '/etc/selinux/targeted/contexts/users/webadm_u'
file5 = '/etc/sudoers'

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    test.createCopyFile(file5)

    file = open(file1, "w")
    file.write('module systemd_webadm 1.0;\n')
    file.write('require {\n')
    file.write('	type webadm_t;\n')
    file.write('	type init_t;\n')
    file.write('	type policykit_t;\n')
    file.write('	type system_dbusd_t;\n')
    file.write('	class capability sys_resource;\n')
    file.write('	class unix_stream_socket connectto;\n')
    file.write('	class dbus send_msg;\n')
    file.write('	class system status;\n')
    file.write('	class process setrlimit;\n')
    file.write('}\n')
    file.write('#============= policykit_t ==============\n')
    file.write('allow policykit_t webadm_t:dbus send_msg;\n')
    file.write('#============= webadm_t ==============\n')
    file.write('allow webadm_t init_t:system status;\n')
    file.write('#!!!! This avc is allowed in the current policy\n')
    file.write('allow webadm_t policykit_t:dbus send_msg;\n')
    file.write('allow webadm_t self:capability sys_resource;\n')
    file.write('#!!!! This avc is allowed in the current policy\n')
    file.write('allow webadm_t system_dbusd_t:dbus send_msg;\n')
    file.write('#!!!! This avc is allowed in the current policy\n')
    file.write('allow webadm_t system_dbusd_t:unix_stream_socket connectto;\n')
    file.write('allow webadm_t self:process setrlimit;\n')
    file.close()
    test.showActionMsg('create file %s' % file1)


    test.runCmdFromRoot(cmd="checkmodule -M -m %s -o %s" % (file1, file2), code=0)
    test.runCmdFromRoot(cmd="semodule_package -o %s -m %s" % (file3, file2), code=0)
    test.runCmdFromRoot(cmd="semodule -i %s" % file3, code=0)


    test.installPack('httpd')


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    test.runCmdFromRoot(cmd="semanage user -a -R 'staff_r system_r webadm_r' -L s0 -r s0 webadm_u", code=0)


    res = test.runCmdFromRoot(cmd='semanage user -l | grep webadm_u', code=0)['output']
    if res == '':
        test.addResult(msg='Неудачная попытка создания пользователя SELinux webadm_u', wait='', taken=res)


    test.runCmdFromRoot(cmd="semanage login -a -r s0 -s webadm_u %s" % firstUser, code=0)

    file = open(file4, "w")
    file.write('system_r:local_login_t:s0 staff_r:staff_t:s0 sysadm_r:sysadm_t:s0\n')
    file.write('system_r:remote_login_t:s0 staff_r:staff_t:s0\n')
    file.write('system_r:sshd_t:s0 staff_r:staff_t:s0 sysadm_r:sysadm_t:s0\n')
    file.write('system_r:crond_t:s0 staff_r:staff_t:s0\n')
    file.write('system_r:xdm_t:s0 staff_r:staff_t:s0\n')
    file.write('staff_r:staff_su_t:s0 staff_r:staff_t:s0\n')
    file.write('staff_r:staff_sudo_t:s0 staff_r:staff_t:s0\n')
    file.write('system_r:initrc_su_t:s0 staff_r:staff_t:s0\n')
    file.write('staff_r:staff_t:s0 staff_r:staff_t:s0\n')
    file.write('sysadm_r:sysadm_su_t:s0 sysadm_r:sysadm_t:s0\n')
    file.write('sysadm_r:sysadm_sudo_t:s0 sysadm_r:sysadm_t:s0\n')
    file.close()
    test.showActionMsg('create file %s' % file1)

    test.runCmdFromRoot("echo '%s ALL=(ALL) TYPE=webadm_t ROLE=webadm_r ALL' >> %s" % (firstUser, file5))

    test.sshConnect(host="127.0.0.1", user=firstUser, passwd=firstUserPass)

    res = test.sshRunCmd(cmd='id -Z', code=0)['output']
    if res != 'webadm_u:staff_r:staff_t:s0':
        test.addResult(msg='Несоответствие контекста безопасности', wait='webadm_u:staff_r:staff_t:s0', taken=res)

    test.sshRunCmd(cmd='echo "# test comm" >> /etc/httpd/conf/httpd.conf', code=1)
    test.sshRunCmd(cmd='echo "Port 20000" >> /etc/ssh/sshd_config', code=1)
    test.sshRunCmd(cmd='systemctl restart httpd', code=1)
    test.sshRunCmd(cmd='systemctl restart sshd', code=1)

    test.sshDisconnect()

    # test.runCmdFromUser(cmd="sudo -s id -Z", code=0)
    # ДОДЕЛАТЬ





except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.exchangeCopyFile(file5)

        test.runCmdFromRoot(cmd='rm %s' % file4, code=0, remov=True)

        test.uninstallPack('httpd')

        test.runCmdFromRoot(cmd='semanage login -d %s' % firstUser, code=0, remov=True)
        test.runCmdFromRoot(cmd='semanage user -d webadm_u', code=0, remov=True)
        test.runCmdFromRoot(cmd='semanage module -r systemd_webadm', code=0, remov=True)

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()

















