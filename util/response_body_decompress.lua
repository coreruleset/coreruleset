require("m")
function main()
        if pcall(require, "zlib") then
                local f = zlib.inflate()
                status, response_body_decompressed = pcall(f, m.getvar("RESPONSE_BODY", "none"))
                if status then
                        m.setvar("tx.response_body_decompressed", response_body_decompressed)
                else
                        m.log(2, "ERROR: decompression of response body failed")
                end
        else
                m.log(2, "ERROR: lua-zlib library not installed, please install it or disable 'decompress_response_body' in crs-setup.conf")
        end
end
