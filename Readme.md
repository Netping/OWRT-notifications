https://netping.atlassian.net/wiki/spaces/NW/pages/3428646916/EPIC3+OWRT+Notifications

ubus send signal '{ "event" : "temperature", "temp" : 71}' - отправка сигнала с "датчика"
ubus send commit '{ "config", "notifyconf" }' - обновление конфига для обновления списка нотификаторов
