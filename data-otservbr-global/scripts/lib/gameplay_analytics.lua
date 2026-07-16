if GameplayAnalytics and GameplayAnalytics.loadComplete then
	return GameplayAnalytics
end

local Analytics = GameplayAnalytics
if not Analytics or not Analytics.coreLoaded then
	Analytics = dofile("data-otservbr-global/scripts/lib/#gameplay_analytics_core.lua")
	Analytics.coreLoaded = true
end

dofile("data-otservbr-global/scripts/lib/#gameplay_analytics_context_impl.lua")
dofile("data-otservbr-global/scripts/lib/#gameplay_analytics_schema_impl.lua")
dofile("data-otservbr-global/scripts/lib/#gameplay_analytics_batching_impl.lua")
dofile("data-otservbr-global/scripts/lib/#gameplay_analytics_reliability_impl.lua")
dofile("data-otservbr-global/scripts/lib/#gameplay_analytics_correctness_impl.lua")

Analytics.loadComplete = true
return Analytics
