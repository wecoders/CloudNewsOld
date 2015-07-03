drop table spider_project;
CREATE TABLE `spider_project` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `queue_name` varchar(30) NULL,
  `status` int(11) NOT NULL DEFAULT '0',
  `process` text NOT NULL,
  `create_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_name` (`name`),
  KEY `ix_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


drop table spider_task;


CREATE TABLE `spider_task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project` varchar(30) NOT NULL,
  `task_id` varchar(100) NOT NULL,
  `url` varchar(1000) NOT NULL,
  `callback` varchar(100) NOT NULL,
  `priority` int(11) NOT NULL DEFAULT '0',
  `last_time` int(11)  NULL DEFAULT NULL,
  `result` text  NULL,
  `status` int(11) NOT NULL,
  `create_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_project` (`project`),
  KEY `ix_url` (`url`),
  KEY `ix_task_id` (`task_id`),
  KEY `ix_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


drop table spider_scheduler;
CREATE TABLE `spider_scheduler` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project` varchar(30) NOT NULL,
  `task_id` varchar(100) NOT NULL,
  `url` varchar(1000) NOT NULL,
  `process` text NOT NULL,
  `next_time` int(11)  NULL DEFAULT NULL,
  `last_time` int(11)  NULL DEFAULT NULL,
  `create_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_project` (`project`),
  KEY `ix_url` (`url`),
  KEY `ix_task_id` (`task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


drop table spider_result;
CREATE TABLE `spider_result` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project` varchar(30) NOT NULL,
  `task_id` varchar(100) NOT NULL,
  `url` varchar(1000) NOT NULL,
  `content` text  NULL,
  `create_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_project` (`project`),
  KEY `ix_task_id` (`task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


alter table spider_project add column `queue_name` varchar(30) NULL;

