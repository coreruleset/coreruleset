require("m")
require("zlib")
function main()
local f = zlib.inflate()
local response_body_uncompressed = f(m.getvar("RESPONSE_BODY", "none"))
m.setvar("tx.response_body_decompressed", response_body_uncompressed)
return nil
end
