require("m")

function main()
	local matched_vars = m.getvars("MATCHED_VARS", "none")
	local rule_severity = tonumber(m.getvar("rule.severity", "none"))
	local rule_severity_name = nil
	local rule_id = m.getvar("rule.id", "none")
	local rule_paranoia_level = tonumber(m.getvar("rule_paranoia_level", "none"))
	local matched_patterns = m.getvar("tx.matched_patterns", "none")
	local score = 0

	if rule_severity == 2 then
		rule_severity_name = "critical"
	elseif rule_severity == 3 then
		rule_severity_name = "error"
	elseif rule_severity == 4 then
		rule_severity_name = "warning"
	elseif rule_severity == 5 then
		rule_severity_name = "notice"
	end

	local patterns = {}
	for p in matched_patterns:gmatch("(.-)|||") do
		table.insert(patterns, p)
	end

	for _, variable in pairs(matched_vars) do
		local add_score = false
		for _, pattern in pairs(patterns) do
			if variable["value"] == pattern then
				add_score = true
			elseif string.find(variable["value"], string.format("^/%s", pattern)) then
				add_score = true
			elseif string.find(variable["value"], string.format("^%s/", pattern)) then
				add_score = true
			elseif string.find(variable["value"], string.format("/%s$", pattern)) then
				add_score = true
			elseif string.find(variable["value"], string.format("%s\0", pattern)) then
				add_score = true
			end
			if add_score then
				m.log(2, string.format("Warning. Matched Data: %s found within %s: %s [id \"%s\"]", pattern, variable["name"], variable["value"], rule_id))
				score = score + tonumber(m.getvar(string.format("tx.%s_anomaly_score", rule_severity_name), "none"))
				break
			end
		end
	end
	if score > 0 then
		m.setvar("tx.lfi_score", tonumber(m.getvar("tx.lfi_score", "none")) + score)
		m.setvar(string.format("tx.anomaly_score_pl%d", rule_paranoia_level), tonumber(m.getvar(string.format("tx.anomaly_score_pl%d", rule_paranoia_level), "none")) + score)
		return "Matched at least one phrase, see previous messages."
	end
	return nil
end
