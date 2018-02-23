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
username VARCHAR(30) BINARY,
login_pass VARCHAR(25) BINARY,
first_name VARCHAR(15),
last_name VARCHAR(15),
e_post VARCHAR(30),
telephone LONG,
is_admin BOOLEAN DEFAULT 0,
PRIMARY KEY(username)
);

CREATE TABLE Maps (
map_id INT auto_increment,
map_creater VARCHAR(30),
title VARCHAR(50),
description TEXT,
start_date TIMESTAMP DEFAULT now(),
end_date DATE,
geo_boundery POLYGON,
zoom int,
PRIMARY KEY(map_id),
FOREIGN KEY (map_creater) REFERENCES Persons(username)
);

CREATE TABLE Maps_Users(
username VARCHAR(30),
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

CREATE TABLE Shapes (
shape_id INT AUTO_INCREMENT,
category_ID INT,
shape_creater VARCHAR(30),
center POINT,
area_or_path LINESTRING,
title VARCHAR(50),
description TEXT,
rate INT DEFAULT 0,
PRIMARY KEY(shape_id, category_ID),
FOREIGN KEY (category_ID) REFERENCES Maps_Categories(category_ID),
FOREIGN KEY (shape_creater) REFERENCES Persons(username)
);


INSERT INTO Persons(username, login_pass, first_name, last_name, e_post, telephone, is_admin) 
VALUES('Mohammed','Mohammed1992','Mohammed','Guniem','mghunime@yahoo.no',004748338891,TRUE);

INSERT INTO Persons(username, login_pass, first_name, last_name, e_post, telephone, is_admin) 
VALUES('Dawit','Dawit1995','Dawit','Kidane','d_kzzz@yahoo.com',0047450088910,TRUE);

INSERT INTO Persons(username, login_pass, first_name, last_name, e_post, telephone) 
VALUES('Rami','Rami1992','Rami','Guniem','rami@yahoo.no',004777665544);

SELECT * FROM Persons WHERE username = 'mohammed' AND login_pass = 'Mohammed1992';

/*
SELECT * FROM Maps_Categories;

INSERT INTO Shapes(category_ID, shape_creater, center, title, description, rate)
VALUES (001, 'Mohammed', POINT(58.969975, 5.73), 'HER TEST', 'BESKRIVELSE TESt', 3);

SELECT *, astext(center) FROM Shapes;


DELETE FROM Shapes WHERE shape_id = 16;

UPDATE Shapes 
SET title = 'hello', description = 'heihei', rate = 2
WHERE shape_id = 1;


SELECT *, astext(area_or_path), astext(center) FROM Shapes;

INSERT INTO Shapes(category_ID, shape_creater, center, area_or_path, title, description, rate)
VALUES(2, 'Mohammed', POINT(0, 0), geomfromtext('LINESTRING(0 0,1 1,2 2)'), 'TITLE', 'DESC', 0);


SELECT S.shape_id, S.shape_creater, astext(S.center), astext(S.area_or_path), S.title, S.description, S.rate, M.category_type, M.category_image_or_color 
FROM Shapes S JOIN Maps_Categories M 
ON S.category_ID = M.category_ID
WHERE map_id = 001;

SELECT * FROM Maps;


SELECT S.shape_id, S.shape_creater, astext(S.center), astext(S.area_or_path), S.title, S.description, S.rate, M.category_type, 
M.category_image_or_color 
FROM Shapes S JOIN Maps_Categories M ON S.category_ID = M.category_ID WHERE map_id = 1;
*/
