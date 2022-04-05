#!/usr/bin/python3
import ubus
import os
import time

# config info
config = "notifyconf"
config_path = "/etc/config/"

try:
    ubus.connect()
except:
    print("Can't connect to ubus")

def test_conf_existance():
    ret = False

    try:
        ret = os.path.isfile(f"{config_path}{config}")
    except:
        assert ret

    assert ret

def test_conf_valid():
    ret = False

    try:
        # ubus.connect()
        confvalues = ubus.call("uci", "get", {"config": config})
        for confdict in list(confvalues[0]['values'].values()):
            #check globals
            if confdict['.type'] == 'globals' and confdict['.name'] == 'globals':
                assert confdict['event'] == [
                    'temperature.Температура', 'userlogin.Вход пользователя', 'userlogout.Выход пользователя',
                    'configchanged.Конфигурация изменена', 'operation.Операция', 'error.Ошибка', 'statechanged.Состояние изменено'
                ]
                assert confdict['method'] == ['email.Почта', 'syslog.Журнал', 'snmptrap.Отправить snmp сообщение', 'sms.Сообщение SMS', 'webhook.Вебхук уведомление']
            #check sensor_prototype
            if confdict['.type'] == 'notify' and confdict['.name'] == 'prototype':
                assert confdict['name'] == 'Notify'
                assert confdict['state'] == '0'
                assert confdict['event'] == 'temperature'
                assert confdict['expression'] == '-'
                assert confdict['method'] == 'email'
                assert confdict['text'] == 'Message text here'
                assert confdict['sendto'] == 'addr1'
                assert confdict['timetable'] == 'datetime1-datetime2'
    except:
        assert ret

def test_ubus_commands():
    ret = False

    #set config items for email method
    try:
        testsection = 'testnotify_email'
        if os.system(f"uci set {config}.{testsection}=notify"):
            raise ValueError("Can't create new section")

        if os.system(f"uci set {config}.{testsection}.name='Notify 1'"):
            raise ValueError("Can't set option name")

        if os.system(f"uci set {config}.{testsection}.state='1'"):
            raise ValueError("Can't set option state")

        if os.system(f"uci set {config}.{testsection}.event='temperature'"):
            raise ValueError("Can't set option event")

        if os.system(f"uci set {config}.{testsection}.expression='%_temp_%>70'"):
            raise ValueError("Can't set option expression")

        if os.system(f"uci set {config}.{testsection}.method='email'"):
            raise ValueError("Can't set option method")

        if os.system(f"uci set {config}.{testsection}.text='Warning: overheat'"):
            raise ValueError("Can't set option text")

        if os.system(f"uci set {config}.{testsection}.sendto='lowpold@gmail.com'"):
            raise ValueError("Can't set option sendto")

        if os.system(f"uci set {config}.{testsection}.timetable='30/08/2021 20:01:13-02/09/2021 20:11:13,30/03/2022 12:15:13-10/04/2022 13:15:13'"):
            raise ValueError("Can't set option timetable")

        #send commit signal for module
        if os.system("ubus send commit '{\"config\":\"" + config + "\"}'"):
            raise ValueError("Can't send commit signal to {config}")

        #wait for notify getting value
        time.sleep(5)
    except:
        assert ret

    #set config items for snmptrap method
    try:
        testsection = 'testnotify_snmptrap'
        if os.system(f"uci set {config}.{testsection}=notify"):
            raise ValueError("Can't create new section")

        if os.system(f"uci set {config}.{testsection}.name='Notify 2'"):
            raise ValueError("Can't set option name")

        if os.system(f"uci set {config}.{testsection}.state='1'"):
            raise ValueError("Can't set option state")

        if os.system(f"uci set {config}.{testsection}.event='temperature'"):
            raise ValueError("Can't set option event")

        if os.system(f"uci set {config}.{testsection}.expression='%_temp_%>70'"):
            raise ValueError("Can't set option expression")

        if os.system(f"uci set {config}.{testsection}.method='snmptrap'"):
            raise ValueError("Can't set option method")

        if os.system(f"uci set {config}.{testsection}.text='Warning: overheat'"):
            raise ValueError("Can't set option text")

        if os.system(f"uci set {config}.{testsection}.sendto='http://dev-sn472763712.tst.netping.tw/'"):
            raise ValueError("Can't set option sendto")

        if os.system(f"uci set {config}.{testsection}.port='162'"):
            raise ValueError("Can't set option sendto")

        if os.system(f"uci set {config}.{testsection}.oid='.0.3.2.1'"):
            raise ValueError("Can't set option sendto")

        if os.system(f"uci set {config}.{testsection}.timetable='30/08/2021 20:01:13-02/09/2021 20:11:13,30/03/2022 12:15:13-10/04/2022 13:15:13'"):
            raise ValueError("Can't set option timetable")

        #send commit signal for module
        if os.system("ubus send commit '{\"config\":\"" + config + "\"}'"):
            raise ValueError("Can't send commit signal to {config}")

        #wait for notify getting value
        time.sleep(5)
    except:
        assert ret

    #set config items for webhook method
    try:
        testsection = 'testnotify_webhook'
        if os.system(f"uci set {config}.{testsection}=notify"):
            raise ValueError("Can't create new section")

        if os.system(f"uci set {config}.{testsection}.name='Notify 3'"):
            raise ValueError("Can't set option name")

        if os.system(f"uci set {config}.{testsection}.state='1'"):
            raise ValueError("Can't set option state")

        if os.system(f"uci set {config}.{testsection}.event='temperature'"):
            raise ValueError("Can't set option event")

        if os.system(f"uci set {config}.{testsection}.expression='%_temp_%>70'"):
            raise ValueError("Can't set option expression")

        if os.system(f"uci set {config}.{testsection}.method='webhook'"):
            raise ValueError("Can't set option method")

        if os.system(f"uci set {config}.{testsection}.text='Warning: overheat'"):
            raise ValueError("Can't set option text")

        if os.system(f"uci set {config}.{testsection}.sendto='http://dev-sn472763712.tst.netping.tw/'"):
            raise ValueError("Can't set option sendto")

        if os.system(f"uci set {config}.{testsection}.request='WEBget'"):
            raise ValueError("Can't set option sendto")

        if os.system(f"uci set {config}.{testsection}.timetable='30/08/2021 20:01:13-02/09/2021 20:11:13,30/03/2022 12:15:13-10/04/2022 13:15:13'"):
            raise ValueError("Can't set option timetable")

        #send commit signal for module
        if os.system("ubus send commit '{\"config\":\"" + config + "\"}'"):
            raise ValueError("Can't send commit signal to {config}")

        #wait for notify getting value
        time.sleep(5)
    except:
        assert ret

    try:
        res = ubus.send("signal", {"event": "temperature", "temp": 71})
        assert res
    except:
        assert ret

    #delete section from config
    print('delete settings')
    os.system(f"uci delete {config}.testnotify_email")
    os.system(f"uci delete {config}.testnotify_snmptrap")
    os.system(f"uci delete {config}.testnotify_webhook")
    os.system(f"uci commit {config}")
    os.system("ubus send commit '{\"config\":\"" + config + "\"}'")
