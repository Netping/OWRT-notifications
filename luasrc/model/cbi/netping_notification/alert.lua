
local config, title = "netping_luci_relay", "Alerts"

m = Map(config, title)
m.template = "netping_notification/alert_list"
m.pageaction = false

return m
