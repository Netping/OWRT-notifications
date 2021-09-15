module("luci.controller.netping_notification.index", package.seeall)

local config = "netping_luci_relay"
local http = require "luci.http"
local uci = require "luci.model.uci".cursor()
local util = require "luci.util"
local log = require "luci.model.netping_notification.log"

local socket = require 'socket'

local relay = require "luci.model.netping_notification.relay.main"
local adapter_list = require "luci.model.netping_notification.relay.adapter_list"

local sys = require "luci.sys"


function notify_backend_on_commit(config_name)
	--sys.exec(string.format("ubus send commit '{\"config\":\"%s\"}", config_name))
	util.ubus(config_name, "send", {config = config_name})
end


function index()
	if nixio.fs.access("/etc/config/netping_luci_relay") then
		entry({"admin", "system", "relay"}, cbi("netping_notification/relay"), "Relays", 30)
		entry({"admin", "system", "alerts"}, cbi("netping_notification/alert"), nil).leaf = true
		entry({"admin", "system", "alerts", "action"}, call("do_action"), nil).leaf = true
	end
end


function get_indication() --[[
	Get operative data using ubus call
	Return the data to web-interface as JSON
]]
	local relay_indication = {
		status = {
			-- ["cfg062442"] = "1"
			-- ["cfg062443"] = "0"
		},
		state = {
			-- ["cfg062442"] = "1"
			-- ["cfg062443"] = "0"
		}
	}
	local ubus_response = {}
	local all_relays = uci:foreach(config, "relay", function(relay)
		if(relay[".anonymous"]) then

			-- Get statuses of all relays
			
			ubus_response = util.ubus("netping_relay", "get_status", {section = string.format("%s", relay[".name"])})
			if(ubus_response and type(ubus_response) == "table" and ubus_response["status"]) then
				relay_indication.status[relay[".name"]] = ubus_response["status"]
			end

			-- Get states of all relays

			ubus_response = util.ubus("netping_relay", "get_state", {section = string.format("%s", relay[".name"])})
			if(ubus_response and type(ubus_response) == "table" and ubus_response["state"]) then
				relay_indication.state[relay[".name"]] = ubus_response["state"]
			end
		end
	end)

	-- Return to web-interface as JSON

	http.prepare_content("application/json")
	http.write(util.serialize_json(relay_indication))
end

function do_relay_action(action, relay_id)

	local payload = {}
	payload["relay_data"] = luci.jsonc.parse(luci.http.formvalue("relay_data"))
	for _, k in pairs({".name", ".anonymous", ".type", ".index"}) do payload["relay_data"][k] = nil end
	payload["globals_data"] = luci.jsonc.parse(luci.http.formvalue("globals_data"))
	payload["adapter_data"] = luci.jsonc.parse(luci.http.formvalue("adapter_data"))

	-- type "logread for debug this:"
	-- if type(payload) == "table" then util.dumptable(payload) else util.perror(payload) end
	local sucsess = false

	local commands = {
		add = function(...)
			relay():new()
		end,
		rename = function(relay_id, payload)
			util.perror(payload["relay_data"]["name"])
			if payload["relay_data"]["name"] then
				relay(relay_id):set("name", payload["relay_data"]["name"])
			end
		end,
		delete = function(relay_id, ...)
			for a_type, adapter in pairs(adapter_list) do
				adapter(relay_id):delete()
			end
			relay(relay_id):delete()
		end,
		switch = function(relay_id, ...)
			local old_state = tonumber(uci:get(config, relay_id, "state"))
			local new_state = (old_state + 1) % 2
			relay(relay_id):set("state", new_state)
		end,
		edit = function(relay_id, payloads)
			-- apply relay settings
			local allowed_relay_options = util.keys(uci:get_all(config, "relay_prototype"))
			for key, value in pairs(payloads["relay_data"]) do
				if util.contains(allowed_relay_options, key) then
					uci:set(config, relay_id, key, value)
				end
			end

			-- apply settings of multiple adapters
			for a_config, a_data in pairs(payload["adapter_data"]) do
				for a_type, adapter in pairs(adapter_list) do
					if(a_config == a_type) then
						--adapter(relay_id):load(a_data)
						adapter(relay_id):set(a_data)
						adapter(relay_id):save()
						adapter(relay_id):commit()
					end
				end
				--success = uci:load(a_config) and uci:commit(a_config)
				--socket.sleep(0.9)
				--success = success or log(a_config .. "commit() error", a_data)
			end


			-- apply settings.globals
			local allowed_global_options = util.keys(uci:get_all(config, "globals"))
			for key, value in pairs(payloads["globals_data"]) do
				if util.contains(allowed_global_options, key) then
					if type(value) == "table" then
						uci:set_list(config, "globals", key, value)
					else
						uci:set(config, "globals", key, value)
					end
				end
			end
		end,
		default = function(...)
			--sucsess = uci:save(config)
			uci:load(config)
			success = uci:load(config) and uci:commit(config)
			success = success or log("uci:commit() error", payload)

			http.prepare_content("text/plain")
			http.write("0")
		end
	}
	if commands[action] then
		commands[action](relay_id, payload)
		commands["default"]()
		notify_backend_on_commit("netping_relay")
	end
end


function do_alert_action(action, alert_id)
	local payload = {}
	payload["alert_data"] = luci.jsonc.parse(luci.http.formvalue("alert_data"))
	local commands = {
		add = function(...)

		end,
		delete = function(alert_id, ...)

		end,
		edit = function(alert_id, payloads)

		end,
		default = function(...)
			http.prepare_content("text/plain")
			http.write("0")
		end
	}
	if commands[action] then
		commands[action](alert_id, payload)
		commands["default"]()
	end
end
