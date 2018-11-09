CREATE TABLE `friend` (
  `friend_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `username` varchar(128) DEFAULT NULL,
  `external_uuid` varchar(128) NOT NULL,
  `image_url` varchar(512) DEFAULT NULL,
  `network_id` int(11) NOT NULL,
  `is_visible` int(11) DEFAULT '1',
  PRIMARY KEY (`friend_id`),
  KEY `FK_network_id_idx` (`network_id`),
  KEY `IX_extermal_uuid` (`external_uuid`),
  CONSTRAINT `FK_network_id` FOREIGN KEY (`network_id`) REFERENCES `network` (`network_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=164 DEFAULT CHARSET=utf8;

CREATE TABLE `message` (
  `message_id` int(11) NOT NULL AUTO_INCREMENT,
  `text` varchar(5120) NOT NULL,
  `external_uuid` varchar(128) NOT NULL,
  `network_id` int(11) NOT NULL,
  `friend_sender_id` int(11) NOT NULL,
  `created_timestamp` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`message_id`),
  KEY `FK_friend_sender_idx` (`friend_sender_id`),
  CONSTRAINT `FK_friend_sender` FOREIGN KEY (`friend_sender_id`) REFERENCES `friend` (`friend_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

CREATE TABLE `network` (
  `network_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `is_active` int(11) NOT NULL,
  `created_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `owner_id` int(11) NOT NULL,
  `network_type` varchar(45) NOT NULL,
  `twitter_id` int(11) DEFAULT NULL,
  `slack_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`network_id`),
  KEY `owner_id_fk_idx` (`owner_id`),
  CONSTRAINT `owner_id_fk` FOREIGN KEY (`owner_id`) REFERENCES `user` (`user_id`) ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;

CREATE TABLE `slack` (
  `slack_id` int(11) NOT NULL AUTO_INCREMENT,
  `workspace` varchar(128) NOT NULL,
  `oauth_access_token` varchar(512) NOT NULL,
  `network_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `friend_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`slack_id`),
  KEY `FK_network_id_idx` (`network_id`),
  KEY `FK_slack_user_id_idx` (`user_id`),
  KEY `FK_slack_friend_id_idx` (`friend_id`),
  CONSTRAINT `FK_slack_friend_id` FOREIGN KEY (`friend_id`) REFERENCES `friend` (`friend_id`) ON DELETE SET NULL ON UPDATE NO ACTION,
  CONSTRAINT `FK_slack_network_id` FOREIGN KEY (`network_id`) REFERENCES `network` (`network_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_slack_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

CREATE TABLE `tweet` (
  `tweet_id` int(11) NOT NULL AUTO_INCREMENT,
  `text` varchar(5120) NOT NULL,
  `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `twitter_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `tweet_uuid` varchar(128) NOT NULL,
  PRIMARY KEY (`tweet_id`),
  KEY `FK_twitter_id_idx` (`twitter_id`),
  KEY `FK_user_id_idx` (`user_id`),
  CONSTRAINT `FK_twitter_id` FOREIGN KEY (`twitter_id`) REFERENCES `twitter` (`twitter_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=122 DEFAULT CHARSET=utf8;

CREATE TABLE `twitter` (
  `twitter_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(128) NOT NULL,
  `consumer_key` varchar(128) NOT NULL,
  `consumer_secret` varchar(128) NOT NULL,
  `access_token` varchar(128) NOT NULL,
  `access_token_secret` varchar(128) NOT NULL,
  `network_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `friend_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`twitter_id`),
  KEY `FK_network_idx` (`network_id`),
  KEY `FK_user_idx` (`user_id`),
  KEY `FK_friend_idx` (`friend_id`),
  CONSTRAINT `FK_friend` FOREIGN KEY (`friend_id`) REFERENCES `friend` (`friend_id`) ON DELETE SET NULL ON UPDATE NO ACTION,
  CONSTRAINT `FK_network` FOREIGN KEY (`network_id`) REFERENCES `network` (`network_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;

CREATE TABLE `user` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(45) NOT NULL,
  `password` varchar(45) NOT NULL,
  `first_name` varchar(45) NOT NULL,
  `last_name` varchar(45) NOT NULL,
  `email` varchar(128) DEFAULT NULL,
  `is_active` int(11) NOT NULL,
  `is_admin` int(11) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
