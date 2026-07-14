function onUpdateDatabase()
	logger.info("Updating database to version 63 (cluster_pending_operations)")

	if not db.tableExists("cluster_pending_operations") then
		if
			not db.query([[
			CREATE TABLE `cluster_pending_operations` (
				`operation_id` char(36) NOT NULL,
				`record_kind` varchar(32) NOT NULL,
				`record_id` int(11) NOT NULL,
				`record_channel_id` int(11) DEFAULT NULL,
				`operation_type` varchar(64) NOT NULL,
				`payload` mediumtext NOT NULL,
				`status` enum('PENDING','APPLIED','FAILED','ABANDONED') NOT NULL DEFAULT 'PENDING',
				`attempts` int(11) NOT NULL DEFAULT '0',
				`last_error` varchar(255) NOT NULL DEFAULT '',
				`enqueued_by_channel_id` int(11) NOT NULL,
				`created_at` bigint(20) NOT NULL,
				`applied_at` bigint(20) DEFAULT NULL,
				CONSTRAINT `cluster_pending_operations_pk` PRIMARY KEY (`operation_id`),
				INDEX `record_lookup` (`record_kind`, `record_id`, `status`),
				INDEX `status_created_at` (`status`, `created_at`)
				-- No FK to players/houses: record_id's meaning depends on
				-- record_kind (a polymorphic reference), the same reasoning
				-- channels.temple_town_id already documents for omitting an FK.
			) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
		]])
		then
			logger.error("Failed to create cluster_pending_operations table.")
			return false
		end
	end

	return true
end
