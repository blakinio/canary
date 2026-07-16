ACCOUNT_TYPE_GAMEMASTER = 4
ACCOUNT_TYPE_GOD = 5

local entrypoints = {
	"data-otservbr-global/scripts/lib/gameplay_analytics.lua",
	"data-otservbr-global/scripts/lib/gameplay_analytics_batching.lua",
	"data-otservbr-global/scripts/lib/gameplay_analytics_context.lua",
	"data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua",
	"data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua",
	"data-otservbr-global/scripts/lib/gameplay_analytics_schema.lua",
}

local function assertCompleteStack(analytics)
	assert(analytics.coreLoaded == true, "gameplay analytics core must be loaded")
	assert(analytics.loadComplete == true, "gameplay analytics stack must be fully loaded")
	assert(analytics.batchingInstalled == true, "batching extension must be installed")
	assert(analytics.contextInstalled == true, "context extension must be installed")
	assert(analytics.correctnessInstalled == true, "correctness extension must be installed")
	assert(analytics.reliabilityInstalled == true, "reliability extension must be installed")
	assert(analytics.schemaGuardInstalled == true, "schema extension must be installed")

	local status = analytics.status()
	assert(status.detailBatchSize == 250, "batching status wrapper must remain installed")
	assert(status.contextSamples == 0, "context status wrapper must remain installed")
	assert(status.dayRollovers == 0, "correctness status wrapper must remain installed")
	assert(status.successfulFlushes == 0, "reliability status wrapper must remain installed")
	assert(status.requiredSchemaVersion == 3, "schema status wrapper must remain installed")
end

for _, firstEntrypoint in ipairs(entrypoints) do
	GameplayAnalytics = nil

	local analytics = dofile(firstEntrypoint)
	assertCompleteStack(analytics)

	local statusFunction = analytics.status
	for _, entrypoint in ipairs(entrypoints) do
		assert(dofile(entrypoint) == analytics, "repeated public entrypoint load must reuse the same analytics table")
	end
	assert(analytics.status == statusFunction, "repeated public entrypoint loading must not replace extension wrappers")
	assertCompleteStack(analytics)
end

print("gameplay analytics load-order tests passed")
