local util = require "luci.util"

function log(title, obj)
	if(obj ~= nil) then
		if(type(obj) == "table") then
			util.perror(title)
			util.perror("====== START ========")
			util.dumptable(obj)
			util.perror("====== END ========")
		else
			util.perror(title .. " = " .. obj)
		end
	else
		util.perror(title)
	end
	return true
end

return log