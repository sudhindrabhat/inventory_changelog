CREATE TABLE `ic_user` (
  `_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'User ID',
  `_unique_id` varchar(20) NOT NULL COMMENT 'Unique ID supplied by client to identify a user',
  `_password_hash` varchar(100) NOT NULL COMMENT 'MD5 hash of the user password',
  `_is_openid` tinyint(1) unsigned NOT NULL COMMENT 'Is Open ID',
  `_ts_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'User signup time',
  PRIMARY KEY (`_id`),
  UNIQUE KEY `UNIQ_unique_id` (`_unique_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

CREATE TABLE `ic_user_session` (
  `_user_id` int(10) unsigned NOT NULL COMMENT 'User ID',
  `_session_hash` varchar(100) NOT NULL COMMENT 'MD5 hash of the user session',
  `_ts_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Time at which session was created',
  KEY `FK_user_session` (`_user_id`),
  CONSTRAINT `FK_user_session` FOREIGN KEY (`_user_id`) REFERENCES `ic_user` (`_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `ic_item` (
  `_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Item ID',
  `_name` varchar(100) NOT NULL COMMENT 'name',
  `_brand` varchar(100) NOT NULL COMMENT 'brand',
  `_category` varchar(100) NOT NULL COMMENT 'category',
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `ic_variant` (
  `_item_id` int(10) unsigned NOT NULL COMMENT 'Item ID',
  `_variant_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'variant ID',
  `_name` varchar(100) NOT NULL COMMENT 'name',
  `_selling_price` decimal(18,8) NOT NULL COMMENT 'selling price',
  `_cost_price` decimal(18,8) NOT NULL COMMENT 'cost price',
  `_quantity` int(10) NOT NULL COMMENT 'quantity',
  `_properties` json NOT NULL COMMENT 'properties',
  KEY `FK_item_variant` (`_item_id`),
  CONSTRAINT `FK_item_variant` FOREIGN KEY (`_item_id`) REFERENCES `ic_item` (`_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `ic_log` (
  `_user_id` int(10) unsigned NOT NULL COMMENT 'User ID',
  `_ts_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Time at which change occurred',
  `_change_type` int(10) unsigned NOT NULL COMMENT 'change type',
  `_change_info` json NOT NULL COMMENT 'changed info',
  KEY `FK_user_session` (`_user_id`),
  CONSTRAINT `FK_user_session` FOREIGN KEY (`_user_id`) REFERENCES `ic_user` (`_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;