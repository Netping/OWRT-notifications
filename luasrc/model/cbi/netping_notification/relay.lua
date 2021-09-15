
local config, title = "netping_luci_relay", "Relays"

m = Map(config, title)
m.template = "netping_notification/relay_list"
m.pageaction = false

return m
