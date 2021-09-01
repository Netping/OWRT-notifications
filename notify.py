import enum
import ubus
import os
from datetime import datetime
from threading import Thread
from threading import Lock




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

class event:
    name = ""
    active = False
    ubus_event = event_type.empty
    date_time = []
    trigger_condition = ''
    notify_method = notify_type.empty
    settings = {}

class notificator:
    events = []
    pollThread = None
    confName = 'notifyconf'
    default_event = event()

    notify_type_map = { 'email' : notify_type.email,
                        'syslog' : notify_type.syslog,
                        'snmptrap' : notify_type.snmptrap,
                        'sms' : notify_type.sms }

    event_type_map = { 'temperature' : event_type.temperature,
                        'userlogin' : event_type.userlogin,
                        'userlogout' : event_type.userlogout }

    mutex = Lock()

    #def __init__(self):
    #    self.applyconfig()

    def unregisterevent(self, ename):
        for e in events:
            if e.name == ename:
                notificator.mutex.acquire()
                events.remove(e)
                notificator.mutex.release()
                return

        print("Can't find event with name \"" + ename + "\"")

    def applyconfig(self):
        notificator.mutex.acquire()

        try:
            ubus.connect()

            confvalues = ubus.call("uci", "get", {"config": notificator.confName})
            for confdict in list(confvalues[0]['values'].values()):
                if confdict['.type'] == 'notify' and confdict['.name'] == 'prototype':
                    notificator.default_event.name = confdict['name']
                    notificator.default_event.active = bool(int(confdict['state']))
                    notificator.default_event.ubus_event = notificator.event_type_map[confdict['event']]
                    try:
                        notificator.default_event.trigger_condition = confdict['trigger']
                    except:
                        notificator.default_event.trigger_condition = ''
                    notificator.default_event.notify_method = notificator.notify_type_map[confdict['method']]
                    #TODO datetime table for event
                    #TODO settings table for event

                if confdict['.type'] == 'notify' and confdict['.name'] != 'prototype':
                    exist = False
                    e = event()
                    e.name = confdict['name']

                    for element in notificator.events:
                        if element.name == e.name:
                            print("Event with name " + e.name + " is exists!")
                            exist = True
                            break

                    if e.name == '':
                        print('Name can\'t be empty')
                        continue

                    if exist:
                        continue

                    try:
                        e.active = bool(int(confdict['state']))
                    except:
                        e.active = notificator.default_event.active
                    e.ubus_event = notificator.event_type_map[confdict['event']]
                    e.trigger_condition = confdict['trigger']
                    e.notify_method = notificator.notify_type_map[confdict['method']]
                    e.date_time = notificator.__parse_timetable(confdict['timetable'])
                    e.settings = notificator.__make_settings(e.notify_method, confdict)

                    if e.ubus_event == event_type.empty:
                        e.ubus_event = notificator.default_event.ubus_event

                    if e.trigger_condition == '':
                        e.trigger_condition = notificator.default_event.trigger_condition

                    if e.notify_method == notify_type.empty:
                        e.notify_method = notificator.default_event.notify_method

                    if not e.date_time:
                        e.date_time = notificator.default_event.date_time

                    if not e.settings:
                        e.settings = notificator.default_event.settings

                    notificator.events.append(e)

                    if not notificator.pollThread:
                        notificator.pollThread = Thread(target=self.__poll, args=())
                        notificator.pollThread.start()

            ubus.disconnect()
        except:
            print("Can't connect to ubus")

        notificator.mutex.release()

    def __parse_timetable(value):
        ret = []

        records = value.split(',')
        for r in records:
            t = r.split('-')
            new = [ datetime.strptime(t[0], "%d/%m/%Y %H:%M:%S"), datetime.strptime(t[1], "%d/%m/%Y %H:%M:%S") ]
            ret.append(new)

        return ret

    def __make_settings(method, dictionary):
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
            pass
        elif method == notify_type.snmptrap:
            pass
        elif method == notify_type.sms:
            pass
        else:
            print('Bad notify type')


        return ret

    def __send_notify(self, e):
        if e.notify_method == notify_type.email:
            try:
                #smtpObj = mailsender()
                for addr in e.settings['toaddr']:
                    #smtpObj.sendmessage(e.settings["fromaddr"], addr, e.settings['message'], e.settings['subject'], e.settings['signature'])
                    os.system('python3 /etc/netping_email/sendtestmail.py --fromaddr ' + e.settings["fromaddr"] + ' --toaddr ' + addr +' --subject ' + e.settings['subject'] + ' --signature ' + e.settings['signature'] + ' --text ' + e.settings['message'])
            except:
                print("Can't send mail")

        else:
            print("Unknown notify type")

    def __handle_event(self, event, data):
        now = datetime.now()

        print("Poll loop")

        notificator.mutex.acquire()

        if not notificator.events:
            print("No events")
            notificator.mutex.release()
            return

        for e in notificator.events:
            print(e.ubus_event)
            if e.active:
                #check event
                if e.ubus_event != notificator.event_type_map[data['event']]:
                    continue
                #TODO check triggers
                #check time
                for t in e.date_time:
                    if now >= t[0] and now <= t[1]:
                        print(e.settings)
                        self.__send_notify(e)

        notificator.mutex.release()

    def __poll(self):
        notificator.mutex.acquire()

        ubus.connect()

        ubus.listen(("signal", self.__handle_event))

        notificator.mutex.release()

        ubus.loop()

        ubus.disconnect()