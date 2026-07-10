local path = "data-otservbr-global/scripts/lib/gameplay_analytics.lua"
local file = assert(io.open(path, "r"), "unable to open " .. path)
local source = file:read("*a")
file:close()

assert(
	not source:match("local%s+result%s*=%s*db%.storeQuery"),
	"analytics persistence must not shadow Canary's global result API"
)
assert(
	source:match("local%s+queryResult%s*=%s*db%.storeQuery"),
	"analytics persistence must store the query handle in queryResult"
)
assert(
	source:match('result%.getNumber%(%s*queryResult%s*,%s*"id"%s*%)'),
	"analytics persistence must read the session id through the global result API"
)
assert(
	source:match("result%.free%(%s*queryResult%s*%)"),
	"analytics persistence must free queryResult through the global result API"
)

print("gameplay analytics persistence validation passed")
