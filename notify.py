import enum
import smtpmail
import ubus
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
        try:
            ubus.connect()
        except:
            print("Can't connect to ubus")

        confvalues = ubus.call("uci", "get", {"config": notificator.confName})
        for confdict in list(confvalues[0]['values'].values()):
            if confdict['.type'] == 'notify' and confdict['.name'] == 'prototype':
                print(confdict)
                notificator.default_event.name = confdict['name']
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

                e.ubus_event = notificator.event_type_map[confdict['event']]
                e.trigger_condition = confdict['trigger']
                e.notify_method = notificator.notify_type_map[confdict['method']]
                #TODO datetime table for event
                #TODO settings table for event

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

                notificator.mutex.acquire()
                notificator.events.append(e)
                notificator.mutex.release()

                if not notificator.pollThread:
                    notificator.pollThread = Thread(target=self.__poll, args=())
                    notificator.pollThread.start()
                
        ubus.disconnect()

    def __send_notify(self, e):
        if e.notify_method == notify_type.email:
            try:
                smtpObj = mailsender()
                smtpObj.sendmessage(e.settings["fromaddr"], 
                                    e.settings["toaddr"], 
                                    e.settings["text"], 
                                    e.settings["subj"],
                                    e.settings["sign"])
            except:
                print("Can't send mail")

        else:
            print("Unknown notify type")

    def __poll(self):
        stop = False
        while not stop:

            #TODO waiting for ubus event
            now = datetime.now()
            notificator.mutex.acquire()

            if not notificator.events:
                stop = True
                notificator.mutex.release()
                continue

            #for e in events:
                #TODO check if current date time in event timetable and ubus event equal option event
                #    self.__send_notify(e)

            notificator.mutex.release()
