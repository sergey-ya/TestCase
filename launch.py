#!/usr/bin/python
# coding: utf_8


import os, sys, json, getopt
import tests.modules as tm


groupLst = [
    dict(num=1, name=u'ФБО «Аудит»', tests=[1, 2, 3, 4, 5, 6, 7, 8]),
    dict(num=2, name=u'ФБО «Защита данных пользователя»', tests=[9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]),
    dict(num=3, name=u'ФБО «Идентификация и аутентификация»', tests=[22, 23, 24, 25, 26, 27, 28, 29, 30]),
    dict(num=4, name=u'ФБО «Управление безопасностью»', tests=[31, 32, 33, 34]),
    dict(num=5, name=u'ФБО «Защита ОО»', tests=[35, 36, 37, 38, 39, 40, 41, 42, 43]),
    dict(num=6, name=u'ФБО «Доступ к ОО»', tests=[44, 45, 46, 47, 48, 49]),
    dict(num=7, name=u'ФБО «Функциональные возможности безопасности операционной системы»', tests=[50]),
    dict(num=8, name=u'ФБО «Использование ресурсов»', tests=[51, 52, 53]),
]

testLst = [
    dict(num=1, name=u'Сигналы нарушения безопасности'),
    dict(num=2, name=u'Генерация данных аудита'),
    dict(num=3, name=u'Просмотр аудита и ограниченный просмотр аудита'),
    dict(num=4, name=u'Выборочный просмотр аудита'),
    dict(num=5, name=u'Избирательный аудит'),
    dict(num=6, name=u'Защищенное хранение журнала аудита'),
    dict(num=7, name=u'Действия в случае возможной потери данных аудита'),
    dict(num=8, name=u'Предотвращение потери данных аудита'),
    dict(num=9, name=u'Дискреционное управление доступом — общий механизм'),
    dict(num=10, name=u'Дискреционное управление доступом — ACL'),
    dict(num=11, name=u'Дискреционное управление доступом — дополнительные правила'),
    dict(num=12, name=u'Ролевое управление доступом'),
    dict(num=13, name=u'Экспорт данных пользователя с атрибутами безопасности'),
    dict(num=14, name=u'Фильтрация сетевого потока'),
    dict(num=15, name=u'Защита остаточной информации — оперативная память'),
    dict(num=16, name=u'Защита остаточной информации — жесткий диск'),
    dict(num=17, name=u'Восстановление информации'),
    dict(num=18, name=u'Уничтожение информации'),
    dict(num=19, name=u'Установка программного обеспечения'),
    dict(num=20, name=u'Правила контроля запуска компонентов программного обеспечения'),
    dict(num=21, name=u'Контроль целостности запускаемых компонентов программного обеспечения'),
    dict(num=22, name=u'Обработка отказов аутентификации'),
    dict(num=23, name=u'Определение атрибутов пользователя'),
    dict(num=24, name=u'Верификация секретов'),
    dict(num=25, name=u'Аутентификация до любых действий пользователя'),
    dict(num=26, name=u'Сочетание механизмов аутентификации'),
    dict(num=27, name=u'Аутентификация с защищенной обратной связью'),
    dict(num=28, name=u'Выбор момента идентификации и идентификация до любых действий пользователя'),
    dict(num=29, name=u'Связывание пользователь-субъект'),
    dict(num=30, name=u'Идентификация объектов доступа'),
    dict(num=31, name=u'Функции управления ФБО'),
    dict(num=32, name=u'Инициализация статических атрибутов'),
    dict(num=33, name=u'Ограниченная по времени авторизация'),
    dict(num=34, name=u'Поддержка наборов базовых конфигураций'),
    dict(num=35, name=u'Конфиденциальность экспортируемых данных ФБО при передаче'),
    dict(num=36, name=u'Тестирование абстрактной машины'),
    dict(num=37, name=u'Верификация целостности'),
    dict(num=38, name=u'Надежные метки времени'),
    dict(num=39, name=u'Ручное восстановление'),
    dict(num=40, name=u'Управление доступом к компонентам ОС'),
    dict(num=41, name=u'Защита хранимой аутентификационной информации'),
    dict(num=42, name=u'Защита от переполнения буфера - выделение памяти'),
    dict(num=43, name=u'Сбой с сохранением безопасного состояния'),
    dict(num=44, name=u'Ограничение на параллельные сеансы'),
    dict(num=45, name=u'Блокирование сеанса, инициированное ФБО'),
    dict(num=46, name=u'Блокирование, инициированное пользователем'),
    dict(num=47, name=u'Завершение сеанса, инициированное ФБО'),
    dict(num=48, name=u'История доступа'),
    dict(num=49, name=u'Открытие сеанса с ОО'),
    dict(num=50, name=u'Блокирование файлов процессами'),
    dict(num=51, name=u'Повышенная отказоустойчивость'),
    dict(num=52, name=u'Ограниченный приоритет обслуживания'),
    dict(num=53, name=u'Максимальные квоты'),
]

resultLst = [
    dict(code=5, header=u'NOT FOUND', desc=u'Файл теста не найден', cl=tm.clStandart),
    dict(code=4, header=u'NOT AUTO', desc=u'Тест невозможно выполнить в автоматическом режиме', cl=tm.clStandart),
    dict(code=10, header=u'FATAL ERROR', desc=u'Произошла критическая ошибка при тестировании', cl=tm.clRed),
    dict(code=2, header=u'ERROR', desc=u'Произошла ошибка при тестировании', cl=tm.clRed),
    dict(code=7, header=u'FAIL ERROR', desc=u'Результаты тестирования не корректны и произошли ошибки во время отката '
                                            u'изменений', cl=tm.clRed),
    dict(code=1, header=u'FAIL', desc=u'Результаты тестирования не корректны', cl=tm.clRed),
    dict(code=3, header=u'WAIT', desc=u'Первая часть теста прошла успешно', cl=tm.clYellow),
    dict(code=6, header=u'OK ERROR', desc=u'Тест прошел успешно, но произошли ошибки во время отката изменений', cl=tm.clGreen),
    dict(code=0, header=u'OK', desc=u'Тест прошел успешно', cl=tm.clGreen),
]



# **********************************************************************************************************************
# TESTING
# **********************************************************************************************************************
def runTest(testInfo=None, stage=0):

    path = os.path.join(os.getcwd(), 'tests/test%s.py' % testInfo['num'])

    ln = tm.showTestName(testInfo['data']['num'], testInfo['data']['name'])
    code = tm.runCmd("sudo -S time python " + path + ' run %s' % stage)['code']
    res = [r['header'] for r in resultLst if r['code'] == code][0]
    cl = [r['cl'] for r in resultLst if r['code'] == code][0]

    tm.showTestRes(res=res, ln=ln, cl=cl)

    return code


def runTestDebug(testInfo=None, stage=0):

    path = os.path.join(os.getcwd(), 'tests/test%s.py' % testInfo['num'])
    code = tm.runCmd("sudo -S python " + path + ' run %s' % stage, True)['code']

    return code


def getTestInfo(testNum=None):

    print "\033[K", testLst[testNum - 1]['name'], "\r",
    sys.stdout.flush()

    path = os.path.join(os.getcwd(), 'tests/test%s.py' % testNum)

    if not os.path.isfile(path):
        return None

    res = tm.runCmd("sudo -S python " + path + ' info')

    if res['code'] == 10:
        return json.loads(res['output'])
    return None


def getTestsInfo(testNumbers=None):

    tm.showMsg(' ')
    tm.showTextCenter(u'\n Получение информации о тестах ', '-')
    params = []
    stages = []
    res = []

    for num in testNumbers:
        testInfo = getTestInfo(num)
        res.append(dict(num=num, data=testInfo))

        if testInfo != None:
            for param in testInfo['params']:
                if not param in params:
                    params.append(param)

            if testInfo['stages'] == 2:
                stages.append(testInfo['num'])

    print "\033[K", 'OK', "\n",
    # tm.showTextCenter('-\n', '-')

    return res, stages, params


def runTesting(testNumbers=None, debug=False, tstLstRes=None, paramsRes=[], stage=0):

    if debug:
        tm.showTextCenter(u'режим отладки')

    if not tm.checkConfigOS():
        sys.exit(20)

    testsInfo, stages, params = getTestsInfo(testNumbers)



    # запуск первого этапа
    if stage == 0:

        tm.checkParams(params) #ПРОВЕРКА

        tm.showMsg(' ')
        tm.showTextCenter(u'\n Тестирование системы \n', '-')
        tm.showMsg(' ')

        tm.writeToLog(type='start_testing', data=dict(os=tm.getOSName(), debug=debug, params=params))

        if len(stages) != 0:
            tm.showTextCenter(u'Запуск первого этапа')
            tm.writeToLog(type='start_stage1')


        tm.delErrorLog()

        for testInfo in testsInfo:

            if testInfo['data']:
                testResult = None
                if not debug:
                    testResult = runTest(testInfo=testInfo, stage=1)
                else:
                    if testInfo['num'] in stages:
                        testResult = runTestDebug(testInfo=testInfo, stage=1)
                    else:
                        testResult = runTestDebug(testInfo=testInfo)

            else:
                tm.showMsg(u'Не удалось получить информацию по тесту')
                testResult = 5


        if len(stages) == 0:
            tm.writeToLog(type='end_testing')
            tm.uncheckParams(params)
        else:
            tm.writeToLog(type='end_stage1')


        if tm.checkErrorLog():
            print(u'В процессе тестирования произошли ошибки (посмотреть: -e / --error)')

        for test in tm.scanLogFile():
            if test['status'] == 3 and tm.getRebootOS():
                print(u'Перезагружаем систему')
                break



    # запуск второго этапа ПРОВЕРКА
    elif stage == 1:

        tm.checkParams(params=params, stage=1)

        tm.showTextCenter(u' Тестирование системы \n', '-')
        tm.showMsg(' ')


        if len(tstLstRes) != 0:
            tm.showTextCenter(u'Результаты первого этапа')

            testsInfoRes = []
            for tst in tstLstRes:
                if tst['status'] == 5:
                    testsInfoRes.append(dict(num=tst['num'], status=tst['status'], data=dict(name=u'Файл теста не найден\n')))
                else:
                    testsInfoRes.append(dict(num=tst['num'], status=tst['status'], data=getTestInfo(tst['num'])))

            for testInfo in testsInfoRes:
                ln = tm.showTestName(testInfo['num'], testInfo['data']['name'])
                res = [r['header'] for r in resultLst if r['code'] == testInfo['status']][0]
                cl = [r['cl'] for r in resultLst if r['code'] == testInfo['status']][0]
                tm.showTestRes(res=res, ln=ln, cl=cl)

            print('\n')


        tm.showTextCenter(u'Запуск второго этапа')
        tm.writeToLog(type='start_stage2')

        resTestCode = None
        for testInfo in testsInfo:
            if not debug:
                resTestCode = runTest(testInfo=testInfo, stage=2)
            else:
                resTestCode = runTestDebug(testInfo=testInfo, stage=2)

        print('\n')

        tm.writeToLog(type='end_stage2')

        tm.uncheckParams(paramsRes)

        if tm.checkErrorLog():
            print(u'В процессе тестирования произошли ошибки (посмотреть: -e / --error)')


    tm.showMsg(' ')



# **********************************************************************************************************************
# INFORMATION
# **********************************************************************************************************************
def outTestList():

    tm.showTextCenter(u'список тестов')
    for group in groupLst:
        tm.showMsg(u'\n%s. %s' % (str(group['num']), group['name']))
        for test in group['tests']:
            tm.showMsg(u'%s. %s' % (testLst[int(test)-1]['num'], testLst[int(test) - 1]['name']))
    tm.showMsg(u' ')


def outHelp():

    tm.showTextCenter(u'справка')

    # tm.showTextCenter(u'ИНФОРМАЦИЯ')
    # print(u'\tДля работы системы необходимы следующие условия:')
    # print(u'\t- запущенный SELinux')
    # print(u'\t- остановленный сервис fileprotect')
    # print(u'\t- установленный пакет python paramiko')
    # print(u'\t- установленный пакет quotatool')
    # print(u'\t- отсутствие пакета python-gssapi')
    # print(u'\t- внешний накопитель с файловой системой ext4')
    # print(u'\t- запущенная удаленная машина\n')

    tm.showTextCenter(u'\nПАРАМЕТРЫ ЗАПУСКА')
    tm.showMsg(u'-a, --all\tЗапуск всех тестов')
    tm.showMsg(u'-g, --group\tЗапуск группы тестов (номер группы, указывается через запятую)')
    tm.showMsg(u'-t, --test\tЗапуск теста (номер теста, указывается через запятую)\n')
    tm.showMsg(u'-l, --list\tВывод списка тестов')
    tm.showMsg(u'-e, --error\tВывод лога с ошибками\n')
    tm.showMsg(u'-d, --debug\tЗапуск в режиме отладки')
    tm.showMsg(u'-с, --clear\tСброс настроек')

    tm.showTextCenter(u'\nСТАТУСЫ ТЕСТОВ')
    for res in resultLst:
        tm.showMsg(u'{cl}{header:<{width}}{endcl}{desc}'.format(cl=res['cl'], header=res['header'],
                                                                endcl=tm.clStandart, width=15, desc=res['desc']))



# **********************************************************************************************************************
# GENERAL
# **********************************************************************************************************************
def checkTestNumbers(testNumbers=None, maxNum=None):

    for num in testNumbers:
        if num > maxNum or num <= 0:
            return False
    return True


try:

    tm.showTextCenter(u'\nРЕД СОФТ - ТЕСТИРОВАНИЕ ОС')

    if not tm.checkCopies():
        tm.showError(u'\n Запуск возможен только одной копии приложения\n')
        sys.exit(27)

    if not tm.checkOS():
        sys.exit(24)

    if not 'root' in tm.runCmd("id -un")['output']:
        tm.showError(u'\n Запуск возможен только с root правами\n')
        sys.exit(21)

    if tm.runCmd('ping ya.ru -c1')['code'] != 0:
        tm.showError(u'\n Запуск возможен только с подключенным интернетом\n')
        sys.exit(26)


    stage = tm.getStage()

    if stage == 1:
        testingData = tm.getTestingData()
        if tm.getRunStage2():
            testNumbers = []
            tstLstRes = []
            for test in tm.scanLogFile():
                if test['status'] == 3:
                    testNumbers.append(test['num'])
                else:
                    tstLstRes.append(dict(num=test['num'], status=test['status']))

            runTesting(testNumbers=testNumbers, tstLstRes=tstLstRes, paramsRes=testingData['params'], debug=testingData['debug'],
                       stage=1)
        else:
            stage = 0
            tm.uncheckParams(testingData['params'])

    if stage == 0:
        options, args = getopt.getopt(sys.argv[1:], 'g:t:ahdlce',
                                      ['group=', 'test=', 'all', 'help', 'debug', 'list', 'clear', 'error'])

        if options == [] and args == []:
            outHelp()

        debug = False

        for opt, value in options:
            if opt in ('-h', '--help'):
                outHelp()

            if opt in ('-l', '--list'):
                outTestList()

            if opt in ('-c', '--clear'):
                if os.path.isfile(os.path.join(os.getcwd(), 'conf')):
                    os.remove(os.path.join(os.getcwd(), 'conf'))
                    tm.showSuccess(u'Настройки удачно очищены.')
                else:
                    tm.showError(u'Файл настроек не найден.')

            if opt in ('-e', '--error'):
                tm.outErrorLog()

            if opt in ('-d', '--debug'):
                debug = True


        run = None
        testNumbers = []

        for opt, value in options:
            if opt in ('-a', '--all'):
                testNumbers = []
                for num in range(1, 54):
                    testNumbers.append(num)
                runTesting(testNumbers, debug)
                run = False
                break

            if opt in ('-g', '--group'):
                lstNum = [int(item) for item in value.split(',')]
                if checkTestNumbers(testNumbers=lstNum, maxNum=8):
                    lstNum = [e for i, e in enumerate(lstNum) if e not in lstNum[:i]]
                    for num in lstNum:
                        testNumbers.extend(groupLst[int(num) - 1]['tests'])
                    run = True
                else:
                    tm.showError(u'Неверно указан номер группы', True)
                    run = False
                    break

            if opt in ('-t', '--test'):
                lstNum = [int(item) for item in value.split(',')]
                if checkTestNumbers(testNumbers=lstNum, maxNum=53):
                    lstNum = [e for i, e in enumerate(lstNum) if e not in lstNum[:i]]
                    testNumbers.extend(lstNum)
                    run = True
                else:
                    tm.showError(u'Неверно указан номер теста', True)
                    run = False
                    break

        if run:
            testNumbers = sorted(testNumbers)
            runTesting(testNumbers, debug)


except getopt.GetoptError as e:
    tm.showError(u'Неверно указаны параметры запуска',  True)
    sys.exit(22)

except Exception as e:
    tm.showError(u'Во время тестирования произошла ошибка')
    tm.showMsg(u'%s\n' % e.message)
    sys.exit(23)

except KeyboardInterrupt:
    tm.showError(u'\n\n Тестирование прервано пользователем\n')
    sys.exit(25)

finally:
    tm.uncheckCopies()


# 20не пройдена проверка конфигурации
# 21необходимы root права
# 22неверно указаны параметры запуска
# 23ошибка во время тетсирования
# 24ос не является разработкой ред-софт
# 25прервано пользователем
# 26не установлено соединение с интернетом
# 27уже запущена копия