--lua5.1-bit32
require("m")
function main(filename)
	local ok, socket = pcall(require, "socket")
	if not ok then
		m.log(2, "ClamAV: lua-socket library not installed, please install it or disable '...' in crs-setup.conf")
		return nil
	end

	local host = "10.10.200.60"
	local port = 3310
	local chunk_size = 4096

	local file_handle = io.open(filename, "r")
	local file_size = file_handle:seek("end")
	if file_size == 0 then
		return nil
	end
	file_handle:seek("set", 0)

	local tcp = socket.tcp()
	tcp:settimeout(2)
	local status, error = tcp:connect(host, port)
	if not status then
		m.log(2, string.format("ClamAV: Error connecting to antivirus: %s", error))
		return nil
	end
	tcp:send("nINSTREAM\n")

	while true do
		local chunk = file_handle:read(chunk_size)
		if chunk then
			tcp:send(string.pack(">I4", string.len(chunk)) .. chunk)
		else
			tcp:send(string.pack(">I4", 0))
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
			m.log(1, string.format("ClamAV: Virus found in uploaded file: %s", virus_name))
			return string.format("ClamAV: Virus found in uploaded file: %s", virus_name)
		else
			m.log2(string.format("ClamAV: Unknown response from antivirus: %s", output))
			return nil
		end
	end
end
