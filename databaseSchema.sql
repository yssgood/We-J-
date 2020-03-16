DROP DATABASE IF EXISTS `WEJ`;
CREATE DATABASE WEJ;

USE WEJ;

DROP TABLE IF EXISTS `User`;
CREATE TABLE User(
    email VARCHAR(25),
    username VARCHAR(25),
    password CHAR(64),
    PRIMARY KEY (email)
);

DROP TABLE IF EXISTS `MusicGroup`;
CREATE TABLE MusicGroup(
    ownerEmail VARCHAR(25), 
    groupName VARCHAR(25), 
    PRIMARY KEY (groupName),
    FOREIGN KEY(ownerEmail) REFERENCES User(email)
);

DROP TABLE IF EXISTS `SavedSongs`;
CREATE TABLE SavedSongs (
    email VARCHAR(25), 
    songID VARCHAR(25),
    PRIMARY KEY(email, songID), 
    FOREIGN KEY(email) REFERENCES User(email)
);