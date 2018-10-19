#!/usr/bin/python
# coding: utf_8

import os
import modules as tm



osf = u'Управление безопасностью'
name = u'Функции управления ФБО'
osfNum = 4
num = 31
stages = 1
params = ['firstUserName']
progress = '2/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # testing-----------------------------------------------------------------------------------------------------------
    test.showTestingBlock()

    def checkAccessFile(path=None, mask=None):
        if os.path.isfile(path):
            msk = test.runCmdFromRoot(cmd="ls -l %s" % path, code=0)['output'][0:11]
            if msk != mask:
                test.addResult(msg=u'Не совпадают права доступа %s' % path, wait=mask, taken=msk)


    def checkAccessFolder(path=None, name=None, mask=None):
        if os.path.exists(path):
            msk = test.runCmdFromRoot(cmd="ls -l %s | grep %s" % (path, name), code=0)['output'][0:11]
            if msk != mask:
                test.addResult(msg=u'Не совпадают права доступа %s%s' % (path, name), wait=mask, taken=msk)


    checkAccessFile(path='/etc/aide.conf', mask='-rw-r-----.')
    checkAccessFile(path='/etc/audit/auditd.conf', mask='-rw-r-----.')
    checkAccessFile(path='/etc/audit/audit.rules', mask='-rw-r-----.')

    checkAccessFolder(path='/etc/', name='cron.d', mask='drwxr-xr-x.')

    checkAccessFile(path='/etc/cron.', mask='-rw-r-----.')
    checkAccessFile(path='/etc/cron.allow', mask='-rw-r-----.')
    checkAccessFile(path='/etc/cron.deny', mask='-rw-------.')
    checkAccessFile(path='/etc/crontab', mask='-rw-r--r--.')
    checkAccessFile(path='/etc/group', mask='-rw-r--r--.')
    # checkAccessFile(path='/etc/gshadow', mask='---------.')
    checkAccessFile(path='/etc/hosts', mask='-rw-r--r--.')
    checkAccessFile(path='/etc/inittab', mask='-rw-r--r--.')
    checkAccessFile(path='/etc/ld.so.conf', mask='-rw-r--r--.')
    # checkAccessFile(path='/etc/localtime', mask='-rw-r-----.')
    checkAccessFile(path='/etc/login.defs', mask='-rw-r--r--.')

    checkAccessFolder(path='/etc/', name='pam.d', mask='drwxr-xr-x.')

    checkAccessFile(path='/etc/passwd', mask='-rw-r--r--.')

    checkAccessFolder(path='/etc/rc.d/', name='init.d', mask='drwxr-xr-x.')

    checkAccessFile(path='/etc/rc.d/init.d/auditd', mask='-rw-r-----.')
    checkAccessFile(path='/etc/securetty', mask='-rw-------.')
    checkAccessFile(path='/etc/security/opasswd', mask='-rw-------.')
    checkAccessFile(path='/etc/selinux/config', mask='-rw-r--r--.')
    checkAccessFile(path='/etc/selinux/semanage.conf', mask='-rw-r--r--.')
    checkAccessFile(path='/etc/selinux/targeted/contexts/users', mask='-rw-r-----.')
    checkAccessFile(path='/etc/shadow', mask='----------.')
    checkAccessFile(path='/etc/ssh/sshd_config', mask='-rw-------.')
    checkAccessFile(path='/etc/stunnel/stunnel.pem', mask='-rw-r-----.')
    checkAccessFile(path='/etc/sysconfig/*', mask='-rw-r-----.')
    checkAccessFile(path='/etc/sysctl.conf', mask='-rw-r--r--.')
    checkAccessFile(path='/etc/vsftpd/ftpusers', mask='-rw-r-----.')
    checkAccessFile(path='/etc/xinetd.conf', mask='-rw-r-----.')
    checkAccessFile(path='/etc/xinetd.d/*', mask='-rw-r-----.')
    checkAccessFile(path='/var/lib/aide/aide.db.gz', mask='-rw-r-----.')
    checkAccessFile(path='/var/lib/aide/aide.db.new.gz', mask='-rw-r-----.')
    checkAccessFile(path='/var/spool/cron/root', mask='-rw-r-----.')

    test.runCmdFromRoot(cmd="cat /etc/gshadow", code=0)
    test.runCmdFirstUser(cmd="cat /etc/gshadow", code=1)

except Exception as e:
    test.showError(e.message)


finally:
    # result out--------------------------------------------------------------------------------------------------------
    test.showResultBlock()

