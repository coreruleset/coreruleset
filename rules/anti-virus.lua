-- Binary packing of numbers into big-endian 4 byte integer (>I4),
-- added for compatibility with Lua version < 5.3.
function clamav_pack_chunk_length(x)
	local bytes = {}
	for j = 1, 4 do
		table.insert(bytes, string.char(x % (2 ^ 8)))
		x = math.floor(x / (2 ^ 8))
	end
	return string.reverse(table.concat(bytes))
end

function main(filename_or_data)
	pcall(require, "m")
	local chunk_size = tonumber(m.getvar("tx.crs_anti-virus_clamav_chunk_size", "none"))
	local connect_type = m.getvar("tx.crs_anti-virus_clamav_connect_type")
	if connect_type == "socket" then
		module_name = "socket.unix"
	elseif connect_type == "tcp" then
		module_name = "socket"
	else
		m.log(2, string.format("ClamAV: invalid value '%s' for 'tx.crs_anti-virus_clamav_connect_type' in crs-setup.conf.", connect_type))
		return nil
	end
	local ok, socket = pcall(require, module_name)
	if not ok then
		m.log(2, "ClamAV: lua-socket library not installed, please install it or disable 'tx.crs_anti-virus_protection_enable' in crs-setup.conf.")
		return nil
	end

	local file_handle = io.open(filename_or_data, "r")
	if file_handle ~= nil then
		data_size = file_handle:seek("end")
		file_handle:seek("set", 0)
	else
		data_size = string.len(filename_or_data)
		position_from = 1
	end
	-- Empty data, nothing to scan.
	if data_size == 0 then
		return nil
	elseif data_size > tonumber(m.getvar("tx.crs_anti-virus_clamav_max_file_size_bytes")) then
		m.log(2, string.format("ClamAV: Scan aborted, data are too big (see 'tx.crs_anti-virus_clamav_max_file_size_bytes' in crs-setup.conf), data size: %s bytes", data_size))
		return nil
	end

	if connect_type == "socket" then
		sck = socket()
	elseif connect_type == "tcp" then
		sck = socket.tcp()
	end
	sck:settimeout(tonumber(m.getvar("tx.crs_anti-virus_clamav_network_timeout_seconds", "none")))
	-- Connecting using unix socket file.
	if connect_type == "socket" then
		status, error = sck:connect(m.getvar("tx.crs_anti-virus_clamav_socket_file"))
	-- Connecting using TCP/IP.
	else
		status, error = sck:connect(m.getvar("tx.crs_anti-virus_clamav_address", "none"), tonumber(m.getvar("tx.crs_anti-virus_clamav_port", "none")))
	end
	if not status then
		m.log(2, string.format("ClamAV: Error connecting to antivirus: %s", error))
		return nil
	end

	sck:send("nINSTREAM\n")

	-- Data needs to be streamed in chunks prefixed by binary packed chunk size.
	-- Streaming is terminated by sending a zero-length chunk.
	-- Chunk size is configurable but must NOT exceed StreamMaxLength defined in ClamAV configuration file.
	while true do
		-- Scanning of uploaded file.
		if file_handle ~= nil then
			chunk = file_handle:read(chunk_size)
		-- Scanning of REQUEST_BODY.
		else
			if position_from > data_size then
				chunk = nil
			else
				local position_to = position_from + chunk_size
				if position_to > data_size then
					position_to = data_size
				end
				chunk = string.sub(filename_or_data, position_from, position_to)
				position_from = position_to + 1
			end
		end
		if chunk then
			-- string.pack was introduced in Lua 5.3 but we need to support older versions.
			--sck:send(string.pack(">I4", string.len(chunk)) .. chunk)
			sck:send(clamav_pack_chunk_length(string.len(chunk)) .. chunk)
		else
			--sck:send(string.pack(">I4", 0))
			sck:send(clamav_pack_chunk_length(0))
			break
		end
	end

	if file_handle ~= nil then
		io.close(file_handle)
	end

	local output = ""
	while true do
		local s, status, partial = sck:receive()
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

	sck:close()

	if output == "stream: OK" then
		return nil
	else
		local virus_name = string.match(output, "^stream: (.+) FOUND$")
		if virus_name then
			m.setvar("tx.virus_name", virus_name)
			return string.format("ClamAV: Virus found in uploaded file: %s", virus_name)
		else
			m.log2(string.format("ClamAV: Unknown response from antivirus: %s", output))
			return nil
		end
	end
end
