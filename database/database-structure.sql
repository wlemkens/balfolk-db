-- phpMyAdmin SQL Dump
-- version 4.5.4.1deb2ubuntu2.1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jul 25, 2019 at 03:19 PM
-- Server version: 10.0.38-MariaDB-0ubuntu0.16.04.1
-- PHP Version: 7.0.33-0ubuntu0.16.04.5

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `balfolk`
--
CREATE DATABASE IF NOT EXISTS `c9balfolk` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `c9balfolk`;

DELIMITER $$

--- --------------------------------------------------------
-
---
--- Drops to the front
---
-
-DROP TABLE IF EXISTS `albums`;
-DROP TABLE IF EXISTS `bands`;
-DROP TABLE IF EXISTS `dances`;
-DROP TABLE IF EXISTS `languages`;
-DROP TABLE IF EXISTS `samples`;
-DROP TABLE IF EXISTS `tracks`;
-DROP TABLE IF EXISTS `tracks_dances`;
-DROP TABLE IF EXISTS `users`;
-
--- --------------------------------------------------------
--
-- Functions
--
DROP FUNCTION IF EXISTS `levenshtein`$$
CREATE FUNCTION `levenshtein` (`s1` VARCHAR(255), `s2` VARCHAR(255)) RETURNS INT(11) BEGIN
        DECLARE s1_len, s2_len, i, j, c, c_temp, cost INT;
        DECLARE s1_char CHAR;
                DECLARE cv0, cv1 VARBINARY(256);

        SET s1_len = CHAR_LENGTH(s1), s2_len = CHAR_LENGTH(s2), cv1 = 0x00, j = 1, i = 1, c = 0;

        IF s1 = s2 THEN
            RETURN 0;
        ELSEIF s1_len = 0 THEN
            RETURN s2_len;
        ELSEIF s2_len = 0 THEN
            RETURN s1_len;
        ELSE
            WHILE j <= s2_len DO
                SET cv1 = CONCAT(cv1, UNHEX(HEX(j))), j = j + 1;
            END WHILE;
            WHILE i <= s1_len DO
                SET s1_char = SUBSTRING(s1, i, 1), c = i, cv0 = UNHEX(HEX(i)), j = 1;
                WHILE j <= s2_len DO
                    SET c = c + 1;
                    IF s1_char = SUBSTRING(s2, j, 1) THEN
                        SET cost = 0; ELSE SET cost = 1;
                    END IF;
                    SET c_temp = CONV(HEX(SUBSTRING(cv1, j, 1)), 16, 10) + cost;
                    IF c > c_temp THEN SET c = c_temp; END IF;
                    SET c_temp = CONV(HEX(SUBSTRING(cv1, j+1, 1)), 16, 10) + 1;
                    IF c > c_temp THEN
                        SET c = c_temp;
                    END IF;
                    SET cv0 = CONCAT(cv0, UNHEX(HEX(c))), j = j + 1;
                END WHILE;
                SET cv1 = cv0, i = i + 1;
            END WHILE;
        END IF;
        RETURN c;
    END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `albums`
--

CREATE TABLE `albums` (
  `id` int(11) NOT NULL,
  `updateid` int(11) DEFAULT NULL,
  `bandid` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `year` int(11) DEFAULT NULL,
  `nb_tracks` int(11) DEFAULT NULL,
  `cover_art` blob,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `added_by` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `bands`
--

CREATE TABLE `bands` (
  `id` int(11) NOT NULL,
  `updateid` int(11) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `url` varchar(255) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `added_by` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `dances`
--

CREATE TABLE `dances` (
  `id` int(11) NOT NULL,
  `parentid` int(11) DEFAULT NULL,
  `languageid` int(11) NOT NULL,
  `nameid` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `level` tinyint(4) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `added_by` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `languages`
--

CREATE TABLE `languages` (
  `id` int(11) NOT NULL,
  `languageid` int(11) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `added_by` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `samples`
--

CREATE TABLE `samples` (
  `id` int(11) NOT NULL,
  `trackid` int(11) NOT NULL,
  `data` longblob NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `added_by` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Stores music samples for determining the dance';

-- --------------------------------------------------------

--
-- Table structure for table `tracks`
--

CREATE TABLE `tracks` (
  `id` int(11) NOT NULL,
  `updateid` int(11) DEFAULT NULL,
  `albumid` int(11) DEFAULT NULL,
  `bandid` int(11) NOT NULL,
  `number` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `bpm` int(11) DEFAULT NULL,
  `level` tinyint(4) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `added_by` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `tracks_dances`
--

CREATE TABLE `tracks_dances` (
  `trackid` int(11) NOT NULL,
  `danceid` int(11) NOT NULL,
  `upvote` int(11) NOT NULL DEFAULT '0',
  `downvote` int(11) NOT NULL DEFAULT '0',
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `added_by` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `salt` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `batch_upload_allowed` tinyint(1) NOT NULL DEFAULT '0',
  `administrator` tinyint(1) NOT NULL DEFAULT '0',
  `moderator` tinyint(1) NOT NULL DEFAULT '0',
  `join_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `banned` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `albums`
--
ALTER TABLE `albums`
  ADD PRIMARY KEY (`id`),
  ADD KEY `bandid` (`bandid`),
  ADD KEY `added_by` (`added_by`),
  ADD KEY `updateid` (`updateid`);

--
-- Indexes for table `bands`
--
ALTER TABLE `bands`
  ADD PRIMARY KEY (`id`),
  ADD KEY `added_by` (`added_by`),
  ADD KEY `updateid` (`updateid`);

--
-- Indexes for table `dances`
--
ALTER TABLE `dances`
  ADD PRIMARY KEY (`nameid`),
  ADD KEY `id` (`id`),
  ADD KEY `languageid` (`languageid`),
  ADD KEY `updateid` (`parentid`);

--
-- Indexes for table `languages`
--
ALTER TABLE `languages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `languageid` (`languageid`),
  ADD KEY `added_by` (`added_by`);

--
-- Indexes for table `samples`
--
ALTER TABLE `samples`
  ADD PRIMARY KEY (`id`),
  ADD KEY `trackid` (`trackid`),
  ADD KEY `added_by` (`added_by`);

--
-- Indexes for table `tracks`
--
ALTER TABLE `tracks`
  ADD PRIMARY KEY (`id`),
  ADD KEY `albumid` (`albumid`),
  ADD KEY `bandid` (`bandid`),
  ADD KEY `added_by` (`added_by`),
  ADD KEY `updateid` (`updateid`);

--
-- Indexes for table `tracks_dances`
--
ALTER TABLE `tracks_dances`
  ADD PRIMARY KEY (`trackid`,`danceid`),
  ADD KEY `trackid` (`trackid`),
  ADD KEY `danceid` (`danceid`),
  ADD KEY `added_by` (`added_by`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `albums`
--
ALTER TABLE `albums`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `bands`
--
ALTER TABLE `bands`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `dances`
--
ALTER TABLE `dances`
  MODIFY `nameid` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `languages`
--
ALTER TABLE `languages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `samples`
--
ALTER TABLE `samples`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `tracks`
--
ALTER TABLE `tracks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `albums`
--
ALTER TABLE `albums`
  ADD CONSTRAINT `album_album` FOREIGN KEY (`updateid`) REFERENCES `albums` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `album_band` FOREIGN KEY (`bandid`) REFERENCES `bands` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `bands`
--
ALTER TABLE `bands`
  ADD CONSTRAINT `band_band` FOREIGN KEY (`updateid`) REFERENCES `bands` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `dances`
--
ALTER TABLE `dances`
  ADD CONSTRAINT `dance_language` FOREIGN KEY (`languageid`) REFERENCES `languages` (`id`);

--
-- Constraints for table `languages`
--
ALTER TABLE `languages`
  ADD CONSTRAINT `language_language` FOREIGN KEY (`languageid`) REFERENCES `languages` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `samples`
--
ALTER TABLE `samples`
  ADD CONSTRAINT `sample_track` FOREIGN KEY (`trackid`) REFERENCES `tracks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `tracks`
--
ALTER TABLE `tracks`
  ADD CONSTRAINT `album_track` FOREIGN KEY (`albumid`) REFERENCES `albums` (`id`),
  ADD CONSTRAINT `band_track` FOREIGN KEY (`bandid`) REFERENCES `bands` (`id`),
  ADD CONSTRAINT `track_track` FOREIGN KEY (`updateid`) REFERENCES `tracks` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `tracks_dances`
--
ALTER TABLE `tracks_dances`
  ADD CONSTRAINT `dance_track` FOREIGN KEY (`danceid`) REFERENCES `dances` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `track_dance` FOREIGN KEY (`trackid`) REFERENCES `tracks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
