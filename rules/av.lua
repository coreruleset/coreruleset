require("m")

function clamav_pack_chunk_length(x)
	local bytes = {}
	for j = 1, 4 do
		table.insert(bytes, string.char(x % (2 ^ 8)))
		x = math.floor(x / (2 ^ 8))
	end
	return string.reverse(table.concat(bytes))
end

function main(filename)
	local connect_timeout = tonumber(m.getvar("tx.crs_anti-virus_clamav_chunk_size", "none"))
	local chunk_size = tonumber(m.getvar("tx.crs_anti-virus_clamav_connect_timeout", "none"))
	local connect_type = m.getvar("tx.crs_anti-virus_clamav_connect_type")
	local module_name = ""
	if connect_type == "socket" then
		socket_file = m.getvar("tx.crs_anti-virus_clamav_socket_file")
		module_name = "socket.unix"
	else
		host = m.getvar("tx.crs_anti-virus_clamav_address", "none")
		port = tonumber(m.getvar("tx.crs_anti-virus_clamav_port", "none"))
		module_name = "socket"
	end
	local ok, socket = pcall(require, module_name)
	if not ok then
		m.log(2, "ClamAV: lua-socket library not installed, please install it or disable 'tx.crs_anti-virus_protection_enable' in crs-setup.conf")
		return nil
	end

	local file_handle = io.open(filename, "r")
	local file_size = file_handle:seek("end")
	if file_size == 0 then
		return nil
	end
	file_handle:seek("set", 0)

	tcp = socket.tcp()
	tcp:settimeout(connect_timeout)
	if connect_type == "socket" then
		status, error = tcp:connect(socket_file)
	else
		status, error = tcp:connect(host, port)
	end
	if not status then
		m.log(2, string.format("ClamAV: Error connecting to antivirus: %s", error))
		return nil
	end

	tcp:send("nINSTREAM\n")

	while true do
		local chunk = file_handle:read(chunk_size)
		if chunk then
			--tcp:send(string.pack(">I4", string.len(chunk)) .. chunk)
			tcp:send(clamav_pack_chunk_length(string.len(chunk)) .. chunk)
		else
			--tcp:send(string.pack(">I4", 0))
			tcp:send(clamav_pack_chunk_length(0))
			break
		end
	end

	io.close(file_handle)

	local output = ""
	while true do
		local s, status, partial = tcp:receive()
		if s then
			output = output .. s
		elseif partial then
			output = output .. partial
		end
		if status == "closed" then
			break
		elseif status == "timeout" then
			m.log(2, "ClamAV: Timeout while scanning file.")
			return nil
		end
	end

	tcp:close()

        if output == "stream: OK" then
		return nil
	else
		local virus_name = string.match(output, "^stream: (.+) FOUND$")
		if virus_name then
			return string.format("ClamAV: Virus found in uploaded file: %s", virus_name)
		else
			m.log2(string.format("ClamAV: Unknown response from antivirus: %s", output))
			return nil
		end
	end
end
