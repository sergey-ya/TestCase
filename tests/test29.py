#!/usr/bin/python
# coding: utf_8


import modules as tm



osf = u'Идентификация и аутентификация'
name = u'Связывание пользователь-субъект'
osfNum = 3
num = 29
stages = 1
params = ['firstUserName', 'secondUserName']
progress = '2/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']
secondUser = test.params['secondUserName']

file1 = '/tmp/suid_test.c'
file2 = '/tmp/suid'
file3 = '/etc/selinux/targeted/contexts/users/webadm_u'
file4 = '/etc/sudoers'

dir1 = '/tmp/iva_dir'

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    test.createCopyFile(file4)

    test.installPack('gcc')

    test.runCmdFromRoot(cmd="usermod -a -G audio %s" % firstUser, code=0)
    test.runCmdFromRoot(cmd="usermod -a -G video %s" % firstUser, code=0)

    file = open(file1, 'w')
    file.write('# define _POSIX_C_SOURCE 200112L\n')
    file.write('#include <stdio.h>\n')
    file.write('#include <sys/types.h>\n')
    file.write('#include <unistd.h>\n')
    file.write('#include <dirent.h>\n')

    file.write('void report (uid_t real) {\n')
    file.write('\tprintf ("Real UID: %d Effective UID: %d\\n", real, geteuid());\n')
    file.write('\t}\n')

    file.write('int list_dir (void){\n')
    file.write('int res = 0;\n')
    file.write('DIR\t\t*dirp;\n')
    file.write('struct dirent\t*directory;\n')
    file.write('dirp = opendir("/home/%s/");\n' % firstUser)
    file.write('\tif (dirp){\n')
    file.write('\t\twhile ((directory = readdir(dirp)) != NULL)\n')
    file.write('\t\t\t{\n')
    file.write('\t\t\tprintf("%s\\n", directory->d_name);\n')
    file.write('\t\t\t}\n')
    file.write('\t}\n')
    file.write('\telse {\n')
    file.write('\t\tprintf("error");\n')
    file.write('\t\tres = 1;\n')
    file.write('\t}\n')
    file.write('closedir(dirp);\n')
    file.write('return res;\n')
    file.write('}\n')

    file.write('int main (void) {\n')
    file.write('\tuid_t real = getuid();\n')
    file.write('\treport(real);\n')
    file.write('\treturn list_dir();\n')
    file.write('}\n')
    file.close()
    test.showActionMsg('create file %s' % file1)

    test.runCmdFromRoot(cmd='gcc %s -o %s' % (file1, file2), code=0)


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()
    tm.showMsg(u'Пункт а')

    # а--------НЕ РАБОТАЕТ ПРОБЛЕМА В СОЗДАНИИ ВТОРИЧНОЙ СЕССИИ ПРИ NEWGRP-----------------------------------
    # test.runCmdFirstUser(cmd='id', code=0)
    # test.runCmdFirstUser(cmd='touch /home/%s/test_file' % firstUser, code=0)
    # test.runCmdFirstUser(cmd='newgrp video', code=0)
    # test.runCmdFirstUser(cmd='touch /home/%s/video_file' % firstUser, code=0)
    # test.runCmdFirstUser(cmd='ls -al /home/%s' % firstUser, code=0)
    # test.runCmdFirstUser(cmd='rm test_file', code=0)
    # test.runCmdFirstUser(cmd='rm video_file', code=0)


    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт б')
    test.runCmdFirstUser(cmd='%s' % file2, code=0)
    test.runCmdSecondUser(cmd='%s' % file2, code=1)

    test.runCmdFromRoot(cmd='chmod u+s %s' % file2, code=0)

    test.runCmdFirstUser(cmd='%s' % file2, code=0)
    test.runCmdSecondUser(cmd='%s' % file2, code=0)


    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт в')
    test.runCmdFirstUser(cmd='id', code=0)
    test.runCmdFirstUser(cmd='id -un', code=0)
    test.runCmdFirstUser(cmd='id -unr', code=0)

    test.runCmdFromRoot(cmd='id', code=0)
    test.runCmdFromRoot(cmd='id -un', code=0)
    test.runCmdFromRoot(cmd='id -unr', code=0)


    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт г')
    test.runCmdFirstUser(cmd='mkdir %s' % dir1, code=0)
    test.runCmdFirstUser(cmd='chmod 777 %s' % dir1, code=0)

    test.runCmdSecondUser(cmd='mkdir %s/pet_dir/' % dir1, code=0)
    test.runCmdSecondUser(cmd='touch %s/text_i.txt' % dir1, code=0)

    test.runCmdFirstUser(cmd='chmod g+s %s' % dir1, code=0)

    test.runCmdSecondUser(cmd='mkdir %s/pet_dir_new/' % dir1, code=0)
    test.runCmdSecondUser(cmd='touch %s/text_p.txt' % dir1, code=0)


    out = test.runCmdFirstUser(cmd='ls -la %s | grep pet_dir' % dir1, code=0)['output'].split('\n')[0]
    if out.find('drwxrwxr-x') == -1 or out.find('%s %s' % (secondUser, secondUser)) == -1:
        test.addResult(msg='Не совпадают параметры pet_dir', wait='drwxrwxr-x', taken=out)

    out = test.runCmdFirstUser(cmd='ls -la %s | grep pet_dir_new' % dir1, code=0)['output'].split('\n')[0]
    if out.find('drwxrwsr-x') == -1 or out.find('%s %s' % (secondUser, firstUser)) == -1:
        test.addResult(msg='Не совпадают параметры pet_dir_new', wait='drwxrwsr-x', taken=out)


    out = test.runCmdFirstUser(cmd='ls -la %s | grep text_i.txt' % dir1, code=0)['output'].split('\n')[0]
    if out.find('-rw-rw-r--') == -1 or out.find('%s %s' % (secondUser, secondUser)) == -1:
        test.addResult(msg='Не сопадают параметры text_i.txt', wait='-rw-rw-r--', taken=out)

    out = test.runCmdFirstUser(cmd='ls -la %s | grep text_p.txt' % dir1, code=0)['output'].split('\n')[0]
    if out.find('-rw-rw-r--') == -1 or out.find('%s %s' % (secondUser, firstUser)) == -1:
        test.addResult(msg='Не сопадают параметры text_p.txt', wait='-rw-rw-r--', taken=out)




    # ------------------------------------------------------------------------------------------------------------------
    tm.showMsg(u'Пункт д')
    test.runCmdFromRoot(cmd='useradd webadmin', code=0)
    test.runCmdFromRoot(cmd='echo "webadmin:qqqwww" | chpasswd', code=0)

    test.runCmdFromRoot(cmd='semanage user -a -R "staff_r system_r webadm_r" -L s0 -r s0 webadm_u', code=0)
    out = test.runCmdFromRoot(cmd='semanage user -l', code=0)['output'].split('\n')
    res = False
    for i in out:
        if i.find('webadm_u') != -1 and i.find('staff_r system_r webadm_r') != -1:
            res = True
            break

    if res == False:
        test.addResult(msg=u'Не удалось создать пользователя SELinux')


    test.sshConnect(host='127.0.0.1', user='webadmin', passwd='qqqwww', port=22)
    context1 = test.sshRunCmd(cmd='id -Z', code=0)['output'].split('\n')[0]
    test.sshDisconnect()

    if context1 != 'unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023':
        test.addResult(msg=u'Несоответствие контекста при первом запросе',
                       wait='unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023', taken=context1)

    test.runCmdFromRoot(cmd='semanage login -a -r s0 -s webadm_u webadmin', code=0)

    file = open(file3, 'w')
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
    test.showActionMsg('create file %s' % file4)


    test.runCmdFromRoot(cmd="echo 'webadmin ALL=(ALL) TYPE=webadm_t ROLE=webadm_r NOPASSWD: ALL' >> %s" % file4, code=0)

    test.sshConnect(host='127.0.0.1', user='webadmin', passwd='qqqwww', port=22)
    context2 = test.sshRunCmd(cmd='id -Z', code=0)['output'].split('\n')[0]
    context3 = test.sshRunCmd(cmd='sudo -s id -Z', code=0)['output'].split('\n')[0]
    test.sshDisconnect()


    if context2 != 'webadm_u:staff_r:staff_t:s0':
        test.addResult(msg=u'Несоответствие контекста безопасности',
                       wait='webadm_u:staff_r:staff_t:s0', taken=context2)

    if context3 != 'webadm_u:webadm_r:webadm_t:s0':
        test.addResult(msg=u'Несоответствие контекста безопасности',
                       wait='webadm_u:webadm_r:webadm_t:s0', taken=context3)


except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()
        # д
        test.exchangeCopyFile(file4)

        test.runCmdFromRoot(cmd='rm %s' % file3, code=0, remov=True)
        test.runCmdFromRoot(cmd='semanage login -d webadmin', code=0, remov=True)
        test.runCmdFromRoot(cmd='semanage user -d webadm_u', code=0, remov=True)
        test.runCmdFromRoot(cmd='userdel -r webadmin', code=0, remov=True)
        # г
        test.runCmdFromRoot(cmd='rm -rf %s' % dir1, code=0, remov=True)
        # а
        test.runCmdFromRoot(cmd='usermod -g %s %s' % (firstUser, firstUser), code=0, remov=True)

        test.runCmdFromRoot(cmd='rm %s' % file2, code=0, remov=True)
        test.runCmdFromRoot(cmd='rm %s' % file1, code=0, remov=True)

        test.runCmdFromRoot(cmd='gpasswd -d %s audio' % firstUser, code=0, remov=True)
        test.runCmdFromRoot(cmd='gpasswd -d %s video' % firstUser, code=0, remov=True)

        test.uninstallPack('gcc')

    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()











