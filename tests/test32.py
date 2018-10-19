#!/usr/bin/python
# coding: utf_8

from modules import runTest
import modules as tm



osf = u'Управление безопасностью'
name = u'Инициализация статических атрибутов'
osfNum = 4
num = 32
stages = 1
params = ['firstUserName']
progress = '3/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)
firstUser = test.params['firstUserName']

file1 = '/home/%s/file1' % firstUser
file2 = '/home/%s/file2' % firstUser
file3 = '/etc/profile'

dir1 = '/home/%s/dir1' % firstUser
dir2 = '/home/%s/dir2' % firstUser

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock()


    # set up------------------------------------------------------------------------------------------------------------
    test.showSetUpBlock()

    test.createCopyFile(file3)



    # testing-----------------------------------------------------------------------------------------------------------

    test.showTestingBlock()

    out1 = test.runCmdFirstUser(cmd="umask -S", code=0)['output'].split('\n')[0]
    if out1 != 'u=rwx,g=rwx,o=rx':
        test.addResult(msg=u'Несоответствие атрибутов по умолчанию', wait='u=rwx,g=rwx,o=rx', taken=out1)


    test.runCmdFirstUser(cmd="mkdir %s" % dir1, code=0)
    test.runCmdFirstUser(cmd="touch %s" % file1, code=0)

    out2 = test.runCmdFirstUser(cmd="ls -ld %s" % dir1, code=0)['output'].split('\n')[0]
    out3 = test.runCmdFirstUser(cmd="ls -l %s" % file1, code=0)['output'].split('\n')[0]
    if out2.find('drwxrwxr-x.') == -1:
        test.addResult(msg=u'Несоответствие прав доступа к %s' % dir1, wait='drwxrwxr-x.', taken=out2)

    if out3.find('-rw-rw-r--.') == -1:
        test.addResult(msg=u'Несоответствие прав доступа к %s' % file1, wait='-rw-rw-r--.', taken=out3)



    tm.changeRowFile(path=file3, oldRow='umask 002', newRow='    umask 077')
    test.showActionMsg('change file %s' % file3)


    out4 = test.runCmdFirstUser(cmd="umask -S", code=0)['output'].split('\n')[0]
    if out4 != 'u=rwx,g=,o=':
        test.addResult(msg=u'Несоответствие атрибутов по умолчанию', wait='u=rwx,g=,o=', taken=out4)


    test.runCmdFirstUser(cmd="mkdir %s" % dir2, code=0)
    test.runCmdFirstUser(cmd="touch %s" % file2, code=0)

    out2 = test.runCmdFirstUser(cmd="ls -ld %s" % dir2, code=0)['output'].split('\n')[0]
    out3 = test.runCmdFirstUser(cmd="ls -l %s" % file2, code=0)['output'].split('\n')[0]
    if out2.find('drwx------.') == -1:
        test.addResult(msg=u'Несоответствие прав доступа к %s' % dir2, wait='drwx------.', taken=out2)

    if out3.find('-rw-------.') == -1:
        test.addResult(msg=u'Несоответствие прав доступа к %s' % file2, wait='-rw-------.', taken=out3)


except Exception as e:
    test.showError(e.message)


finally:
    try:
        # clear---------------------------------------------------------------------------------------------------------
        test.showEndBlock()

        test.exchangeCopyFile(file3)

        test.runCmdFromRoot(cmd='rm %s' % file2, code=0, remov=True)
        test.runCmdFromRoot(cmd='rm %s' % file1, code=0, remov=True)

        test.runCmdFromRoot(cmd='rm -rf %s' % dir2, code=0, remov=True)
        test.runCmdFromRoot(cmd='rm -rf %s' % dir1, code=0, remov=True)
    except Exception as e:
        test.showError(e.message)

    finally:
        # result out----------------------------------------------------------------------------------------------------
        test.showResultBlock()



