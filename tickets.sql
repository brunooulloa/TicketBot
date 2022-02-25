CREATE DATABASE `tickets`;
USE `tickets`;

CREATE TABLE `tickets` (
  `ticket_id` int(11) NOT NULL AUTO_INCREMENT,
  `ticket_creator` varchar(255) DEFAULT NULL,
  `ticket_creator_id` bigint(20) DEFAULT NULL,
  `closed` binary(1) DEFAULT '0',
  PRIMARY KEY (`ticket_id`)
) ENGINE = InnoDB AUTO_INCREMENT = 126 DEFAULT CHARSET=utf8mb4;
