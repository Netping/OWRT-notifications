#!/usr/bin/python3
import enum
import ubus
import os
import re
from datetime import datetime
from threading import Thread
from threading import Lock
from journal import journal




class notify_type(enum.Enum):
    empty = 0
    email = 1
    syslog = 2
    snmptrap = 3
    sms = 4

class event_type(enum.Enum):
    empty = 0
    temperature = 1
    userlogin = 2
    userlogout = 3
    configchanged = 4
    operation = 5
    error = 6
    statechanged = 7

class event:
    name = ""
    active = False
    ubus_event = event_type.empty
    date_time = []
    expression = ''
    notify_method = notify_type.empty
    settings = {}

module_name = "Notifications"

events = []
pollThread = None
ubusConnected = False
confName = 'notifyconf'
default_event = event()

notify_type_map = { 'email' : notify_type.email,
                    'syslog' : notify_type.syslog,
                    'snmptrap' : notify_type.snmptrap,
                    'sms' : notify_type.sms }

event_type_map = { 'temperature' : event_type.temperature,
                    'userlogin' : event_type.userlogin,
                    'userlogout' : event_type.userlogout,
                    'configchanged' : event_type.configchanged,
                    'operation' : event_type.operation,
                    'error' : event_type.error,
                    'statechanged' : event_type.statechanged }

mutex = Lock()

def handle_event(event, data):
    now = datetime.now()

    mutex.acquire()

    if not events:
        mutex.release()
        return

    for e in events:
        if e.active:
            #check event
            if e.ubus_event != event_type_map[data['event']]:
                continue
            #check expression
            expr = expression_convert(e.expression)
            expr_res = eval(expr)
            if not expr_res:
                continue
            #check time
            for t in e.date_time:
                if now >= t[0] and now <= t[1]:
                    send_notify(e)

    mutex.release()

def reconfigure(event, data):
    if data['config'] == confName:
        mutex.acquire()

        del events[:]

        mutex.release()

        journal.WriteLog(module_name, "Normal", "notice", "Config changed!")

        applyconfig()

def poll():
    global ubusConnected

    mutex.acquire()

    ubus.connect()

    ubusConnected = True

    ubus.listen(("signal", handle_event))
    ubus.listen(("commit", reconfigure))

    mutex.release()

    ubus.loop()

    ubus.disconnect()

    ubusConnected = False

def parse_timetable(value):
    ret = []

    records = value.split(',')
    for r in records:
        t = r.split('-')
        new = [ datetime.strptime(t[0], "%d/%m/%Y %H:%M:%S"), datetime.strptime(t[1], "%d/%m/%Y %H:%M:%S") ]
        ret.append(new)

    return ret

def make_settings(method, dictionary):
    ret = {}

    if method == notify_type.email:
        try:
            ret['message'] = dictionary['text']
        except:
            ret['message'] = ''

        try:
            ret['fromaddr'] = dictionary['from']
        except:
            ret['fromaddr'] = ''

        try:
            ret['subject'] = dictionary['subject']
        except:
            ret['subject'] = ''

        try:
            ret['signature'] = dictionary['signature']
        except:
            ret['signature'] = ''

        try:
            ret['toaddr'] = [ a for a in dictionary['sendto'].split(',')]
        except:
            ret['toaddr'] = []

    elif method == notify_type.syslog:
        try:
            ret['message'] = dictionary['text']
        except:
            ret['message'] = ''

        try:
            ret['level'] = dictionary['loglevel']
        except:
            ret['level'] = ''

        try:
            ret['prefix'] = dictionary['logprefix']
        except:
            ret['prefix'] = ''

    elif method == notify_type.snmptrap:
        pass
    elif method == notify_type.sms:
        pass
    else:
        journal.WriteLog(module_name, "Normal", "error", "Bad notify type")

    return ret

def applyconfig():
    global pollThread
    global ubusConnected

    mutex.acquire()

    try:
        if not ubusConnected:
            ubus.connect()

        confvalues = ubus.call("uci", "get", {"config": confName})
        for confdict in list(confvalues[0]['values'].values()):
            if confdict['.type'] == 'notify' and confdict['.name'] == 'prototype':
                default_event.name = confdict['name']
                default_event.active = bool(int(confdict['state']))
                default_event.ubus_event = event_type_map[confdict['event']]
                try:
                    default_event.expression = confdict['expression']
                except:
                    default_event.expression = ''
                default_event.notify_method = notify_type_map[confdict['method']]

            if confdict['.type'] == 'notify' and confdict['.name'] != 'prototype':
                exist = False
                e = event()
                e.name = confdict['name']

                for element in events:
                    if element.name == e.name:
                        journal.WriteLog(module_name, "Normal", "error", "Event with name " + e.name + " is exists!")
                        exist = True
                        break

                if e.name == '':
                    journal.WriteLog(module_name, "Normal", "error", "Name can't be empty")
                    continue

                if exist:
                    continue

                try:
                    e.active = bool(int(confdict['state']))
                except:
                    e.active = default_event.active

                e.ubus_event = event_type_map[confdict['event']]
                e.expression = confdict['expression']

                e.notify_method = notify_type_map[confdict['method']]
                e.date_time = parse_timetable(confdict['timetable'])
                e.settings = make_settings(e.notify_method, confdict)

                if e.ubus_event == event_type.empty:
                    e.ubus_event = default_event.ubus_event

                if e.expression == '':
                    e.expression = default_event.expression

                if e.notify_method == notify_type.empty:
                    e.notify_method = default_event.notify_method

                if not e.date_time:
                    e.date_time = default_event.date_time

                if not e.settings:
                    e.settings = default_event.settings

                events.append(e)

        if not ubusConnected:
            ubus.disconnect()

        if not pollThread:
            pollThread = Thread(target=poll, args=())
            pollThread.start()

    except Exception as ex:
        journal.WriteLog(module_name, "Normal", "error", "Can't connect to ubus " + str(ex))

    mutex.release()

def send_notify(e):
    if e.notify_method == notify_type.email:
        try:
            for addr in e.settings['toaddr']:
                ubus.call("owrt_email", "send_mail", { "fromaddr":e.settings['fromaddr'], "toaddr":addr, "text":e.settings['message'], "subject":e.settings['subject'] ,"signature":e.settings['signature'], "ubus_rpc_session":"1" })
        except Exception as ex:
            journal.WriteLog(module_name, "Normal", "error", "Can't send mail" + str(ex))

    elif e.notify_method == notify_type.syslog:
        try:
            journal.WriteLog(e.settings['prefix'], "Normal", e.settings['level'], e.settings['message'])
        except:
            journal.WriteLog(module_name, "Normal", "error", "Can't write log")
    else:
        journal.WriteLog(module_name, "Normal", "error", "Unknown notify type")

def expression_convert(expression):
    result = re.findall(r'%_(\S+)_%', expression)
    result = set(result)

    for r in result:
        expression = expression.replace("%_" + r + "_%", "data['" + r + "']")

    logic_operands = [ 'AND', 'OR', 'NOT' ]

    for l in logic_operands:
        expression = expression.replace(l, l.lower())

    expression = expression.replace("=", "==")

    return expression

def main():
    applyconfig()

if __name__ == "__main__":
    main()
