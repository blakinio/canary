if GameplayAnalytics and GameplayAnalytics.coreLoaded then
	return GameplayAnalytics
end

local Analytics = dofile("data-otservbr-global/scripts/lib/#gameplay_analytics_core.lua")
Analytics.coreLoaded = true
return Analytics
