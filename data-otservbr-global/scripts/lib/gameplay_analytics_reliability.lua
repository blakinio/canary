local Analytics = GameplayAnalytics
if not Analytics or not Analytics.coreLoaded then
	Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics.lua")
end

return dofile("data-otservbr-global/scripts/lib/#gameplay_analytics_reliability_impl.lua")
