DROP DATABASE IF EXISTS `WEJ`;
CREATE DATABASE WEJ;

USE WEJ;

DROP TABLE IF EXISTS `User`;
CREATE TABLE User(
    email VARCHAR(25),
    username VARCHAR(25),
    password CHAR(64),
    PRIMARY KEY (email, username)
);

DROP TABLE IF EXISTS `MusicGroup`;
CREATE TABLE MusicGroup(
    email VARCHAR(25), 
    username VARCHAR(25),
    groupName VARCHAR(25), 
    PRIMARY KEY (email, groupName)
);