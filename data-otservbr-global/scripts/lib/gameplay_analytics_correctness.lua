if GameplayAnalytics and not GameplayAnalytics.coreLoaded and not GameplayAnalytics.loadComplete then
	return dofile("data-otservbr-global/scripts/lib/#gameplay_analytics_correctness_impl.lua")
end

return dofile("data-otservbr-global/scripts/lib/gameplay_analytics.lua")
