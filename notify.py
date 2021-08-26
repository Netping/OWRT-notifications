import enum
import smtpmail
import ubus




class notify_type(enum.Enum):
    email = 0
    syslog = 1
    snmptrap = 2


class notificator:
    events = []

    def __init__(self):
        self.__notify_method = notify_type.email
        self.senders_settings = { notify_type.email :  { "fromaddr" : "", "toaddr" : "", "subj" : "", "text" : "", "sign" : "" },
                        notify_type.syslog : { "prefix" : "" },
                        notify_type.snmptrap : { "prefix" : "" } }

    def setnotifymethod(self, method):
        self.__notify_method = method

    def registerevent(self, event):
        pass

    def __send_notify(self):
        if self.__notify_method == notify_type.email:
            try:
                smtpObj = mailsender()
                smtpObj.sendmessage(self.senders_settings[notify_type.email]["fromaddr"], 
                                    self.senders_settings[notify_type.email]["toaddr"], 
                                    self.senders_settings[notify_type.email]["text"], 
                                    self.senders_settings[notify_type.email]["subj"],
                                    self.senders_settings[notify_type.email]["sign"])
            except:
                print("Can't send mail")

        else:
            print("Unknown notify type")
