#!/usr/bin/python
# coding: utf_8

import time, os
from datetime import datetime
from subprocess import check_output
import modules as tm

osf = u'Защита данных пользователя'
name = u'Защита остаточной информации — оперативная память'
osfNum = 2
num = 15
stages = 0
params = []
progress = '0/3'


testInfo = dict(osf=osf, name=name, osfNum=osfNum, num=num, stages=stages, params=params)

tm.launchTest(testInfo)

test = tm.runTest(testInfo)

try:
    # info--------------------------------------------------------------------------------------------------------------
    test.showInfoBlock(auto=False)

    # NOT AUTOMATIC
    # снимки virtualBox

    tm.showTextCol([u'Установить или перенести установленную ОС в среду виртуализации VirtualBox (версии 5.0 и старше).\n'])

    tm.showTextCol([u'На ЭВМ2 создать файл /tmp/test_mem.c следующего содержания:'])
    tm.showTextCol([u'#include<stdio.h>'])
    tm.showTextCol([u'int main(void)'])
    tm.showTextCol([u'{'])
    tm.showTextCol([u'int i =10;'])
    tm.showTextCol([u'while (i){'])
    tm.showTextCol([u'   char st[] = "test clean proc";'])
    tm.showTextCol([u'   sleep (1);'])
    tm.showTextCol([u'   i--;'])
    tm.showTextCol([u'   }'])
    tm.showTextCol([u'   return 0;'])
    tm.showTextCol([u'}\n'])

    tm.showTextCol([u'Скомпилировать созданный файл командой:'])
    tm.showTextCol([u'gcc /tmp/test_mem.c -o /tmp/tstmem\n'])

    tm.showTextCol([u'Скомпилированный исполняемый файл tstmem перенести в виртуальную ОС вкаталог tmp.\n'])

    tm.showTextCol([u'Запустить виртуальную ОС. В главном меню среды виртуализации VirtualBox выбрать «Машина» - '
                    u'«Приостановить», далее «Машина» - «Сделать снимок состояния».\n'])

    tm.showTextCol([u'Дождаться завершения выполнения снимка. Зарегистрироваться в ОС под учетной записью пользователя '
                    u'ivanov. В графическом сеансе открыть текстовый редактор Pluma и в рабочей области ввести текст:'])
    tm.showTextCol([u'test memory clean\n'])

    tm.showTextCol([u'Не закрывая текстовый редактор, свернуть его в панель задач. От имени пользователя ivanov в '
                    u'терминале выполнить команду:'])
    tm.showTextCol([u'[ivanov@goslinux ~]$ /tmp/tstmem\n'])

    tm.showTextCol([u'Программа должна выполняться 10 секунд. Сразу после старта программы, не дожидаясь ее завершения '
                    u'приостановить работу виртуальной ОС и сделать снимок состояния виртуальной ОС. Дождаться '
                    u'завершения выполнения снимка и возобновить работу ОС.\n'])

    tm.showTextCol([u'После завершения выполнения программы tstmem закрыть терминал и текстовый редактор Pluma, '
                    u'отказавшись от сохранения данных.\n'])

    tm.showTextCol([u'Приостановить работу виртуальной ОС и сделать снимок.\n'])

    tm.showTextCol([u'В хост-системе на базе которой развернута среда виртуализации перейти в каталог хранения '
                    u'снимков ОС и выполнить команду поиска ключевых фраз в снимках:'])
    tm.showTextCol([u'/Snapshots $ grep -c "test memory clean" *.*'])
    tm.showTextCol([u'/Snapshots $ grep -c "test clean proc" *.*'])



    # result------------------------------------------------------------------------------------------------------------
    test.showResultBlock2()
    tm.showTextCol([u'При освобождении оперативной памяти происходит очистка. В созданных снимках виртуальных ОС: '
                    u'искомые комбинации встречаются по одному разу — в тех снимках которые были сделаны в момент '
                    u'когда был открыт текстовый редактор и запущено тестовое приложение. В снимках ОС, до и после '
                    u'этого момента искомых комбинаций нет.\n'])

    tm.showTextCol([u'{0f85010a-ac19-42ca-abf9-8acb6ccafa62}.vmdk:0'])
    tm.showTextCol([u'2017-10-27T14-10-59-914372000Z.sav:0'])
    tm.showTextCol([u'2017-10-27T14-13-08-861134000Z.sav:1'])
    tm.showTextCol([u'2017-10-27T14-13-37-493221000Z.sav:0'])
    tm.showTextCol([u'{901a9f21-0181-4a29-9c2f-5330f391d42f}.vmdk:0'])
    tm.showTextCol([u'{f94406e4-93df-4ecc-8c26-afcbbe49fa9c}.vmdk:0'])



except Exception as e:
    test.showError(e.message)


finally:
    test.showCanNotResultBlock()
