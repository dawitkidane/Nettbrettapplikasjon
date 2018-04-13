DROP SCHEMA sql2217838;
CREATE SCHEMA sql2217838;
USE sql2217838;

/*
Server: sql2.freemysqlhosting.net
Name: sql2217838
Username: sql2217838
Password: cR3!bC4!
Port number: 3306


ACCOUNT
m.guniem@stud.uis.no
mohammed?!?!?
*/

CREATE TABLE Persons (
username VARCHAR(20),
login_pass VARCHAR(20),
first_name VARCHAR(20),
last_name VARCHAR(20),
e_post VARCHAR(30),
telephone LONG,
PRIMARY KEY(username)
);

CREATE TABLE Maps (
map_id INT auto_increment,
map_creater VARCHAR(20),
title VARCHAR(40),
description TEXT,
start_date TIMESTAMP DEFAULT now(),
end_date DATE,
geo_boundery POLYGON,
zoom INT,
PRIMARY KEY(map_id),
FOREIGN KEY (map_creater) REFERENCES Persons(username)
);

CREATE TABLE Maps_Interviewers(
username VARCHAR(20),
map_id INT,
PRIMARY KEY (username, map_id),
FOREIGN KEY (username) REFERENCES Persons(username),
FOREIGN KEY (map_id) REFERENCES Maps(map_id)
);

CREATE TABLE Maps_Administrators(
username VARCHAR(20),
map_id INT,
PRIMARY KEY (username, map_id),
FOREIGN KEY (username) REFERENCES Persons(username),
FOREIGN KEY (map_id) REFERENCES Maps(map_id)
);

CREATE TABLE Maps_Categories(
category_ID INT AUTO_INCREMENT,
category_name VARCHAR(30),
category_type VARCHAR(30),
category_image_or_color VARCHAR(30),
map_id INT,
PRIMARY KEY (category_ID),
FOREIGN KEY (map_id) REFERENCES Maps(map_id)
);

CREATE TABLE Maps_Questions(
question_ID INT AUTO_INCREMENT,
question Text,
map_id INT,
PRIMARY KEY (question_ID),
FOREIGN KEY (map_id) REFERENCES Maps(map_id)
);

CREATE TABLE Maps_Respondents(
respondent_ID INT AUTO_INCREMENT,
map_id INT,
PRIMARY KEY (respondent_ID, map_id),
FOREIGN KEY (map_id) REFERENCES Maps(map_id)
);

CREATE TABLE Respondent_Answers(
respondent_ID INT,
question_ID INT,
Answer TEXT,
PRIMARY KEY(respondent_ID, question_ID),
FOREIGN KEY (respondent_ID) REFERENCES Maps_Respondents(respondent_ID),
FOREIGN KEY (question_ID) REFERENCES Maps_Questions(question_ID)
);

CREATE TABLE Shapes (
shape_id INT AUTO_INCREMENT,
category_ID INT,
shape_creater VARCHAR(20),
center POINT,
area_or_path LINESTRING,
title VARCHAR(40),
description TEXT,
rate INT DEFAULT 0,
respondent_ID INT,
PRIMARY KEY(shape_id),
FOREIGN KEY (category_ID) REFERENCES Maps_Categories(category_ID),
FOREIGN KEY (shape_creater) REFERENCES Persons(username),
FOREIGN KEY (respondent_ID) REFERENCES Maps_Respondents(respondent_ID)
);

CREATE TABLE Feedbacks (
feedback_id INT AUTO_INCREMENT,
map_id INT,
user VARCHAR(20),
date TIMESTAMP DEFAULT now(),
cmt VARCHAR(30000),
PRIMARY KEY (feedback_id),
FOREIGN KEY (user) REFERENCES Persons(username),
FOREIGN KEY (map_id) REFERENCES Maps(map_id)

);

INSERT INTO Persons(username, login_pass, first_name, last_name, e_post, telephone) 
VALUES('Mohammed','Mohammed1992','Mohammed','Guniem','mghunime@yahoo.no',004748338891);

INSERT INTO Persons(username, login_pass, first_name, last_name, e_post, telephone) 
VALUES('Dawit','Dawit1995','Dawit','Kidane','d_kzzz@yahoo.com',0047450088910);

INSERT INTO Persons(username, login_pass, first_name, last_name, e_post, telephone) 
VALUES('Rami','Rami1992','Rami','Guniem','rami@yahoo.no',004777665544);

CREATE FULLTEXT INDEX Text_Search_Index ON Persons(username, first_name, last_name, e_post, telephone);

SELECT username FROM Persons WHERE match(username) against('mo');


