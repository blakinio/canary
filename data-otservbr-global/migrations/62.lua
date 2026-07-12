function onUpdateDatabase()
	logger.info("Updating database to version 62 (account-wide quest persistence and migration audit)")

	if not db.query([[
		CREATE TABLE IF NOT EXISTS `account_quest_access` (
			`account_id` INT(11) UNSIGNED NOT NULL,
			`quest_id` VARCHAR(128) NOT NULL,
			`unlocked_by` INT(11) NOT NULL DEFAULT 0,
			`unlocked_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
			PRIMARY KEY (`account_id`, `quest_id`),
			CONSTRAINT `account_quest_access_account_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
	]]) then
		return false
	end

	if not db.query([[
		CREATE TABLE IF NOT EXISTS `account_quest_rewards` (
			`account_id` INT(11) UNSIGNED NOT NULL,
			`player_id` INT(11) NOT NULL DEFAULT 0,
			`quest_id` VARCHAR(128) NOT NULL,
			`reward_mode` VARCHAR(32) NOT NULL,
			`claimed_by` INT(11) NOT NULL DEFAULT 0,
			`claimed_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
			PRIMARY KEY (`account_id`, `quest_id`, `reward_mode`, `player_id`),
			CONSTRAINT `account_quest_rewards_account_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
	]]) then
		return false
	end

	return db.query([[
		CREATE TABLE IF NOT EXISTS `account_quest_migrations` (
			`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
			`migration_type` VARCHAR(32) NOT NULL,
			`old_value` VARCHAR(128) NOT NULL,
			`new_value` VARCHAR(128) NOT NULL,
			`rows_affected` INT UNSIGNED NOT NULL DEFAULT 0,
			`executed_by` VARCHAR(128) NOT NULL DEFAULT 'tool',
			`executed_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
			PRIMARY KEY (`id`)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
	]])
end
