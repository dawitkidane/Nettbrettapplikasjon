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
username VARCHAR(30),
login_pass VARCHAR(25),
first_name VARCHAR(15),
last_name VARCHAR(15),
e_post VARCHAR(30),
telephone LONG,
is_admin BOOLEAN,
PRIMARY KEY(username)
);

CREATE TABLE Maps (
map_id INT auto_increment,
map_creater VARCHAR(30),
start_date TIMESTAMP DEFAULT now(),
end_date DATE,
geo_boundery POLYGON,
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

CREATE TABLE Shapes (
shape_id INT auto_increment,
shape_creater VARCHAR(30),
map_id INT,
icon TEXT,
shape_type VARCHAR(5),
center POINT,
area_or_path LINESTRING,
title VARCHAR(50),
description TEXT,
rate INT DEFAULT 0,
PRIMARY KEY(shape_id, map_id),
FOREIGN KEY (map_id) REFERENCES Maps(map_id),
FOREIGN KEY (shape_creater) REFERENCES Persons(username)
);


INSERT INTO Persons(username, login_pass, first_name, last_name, e_post, telephone, is_admin) 
VALUES('Mohammed','Mohammed1992','Mohammed','Guniem','mghunime@yahoo.no',004748338891,TRUE);

INSERT INTO Persons(username, login_pass, first_name, last_name, e_post, telephone, is_admin) 
VALUES('Rami','Rami1992','Rami','Guniem','rami@yahoo.no',004777665544,FALSE);

INSERT INTO Maps(map_creater, end_date, geo_boundery) 
VALUES('Mohammed','2018-05-15',GEOMFROMTEXT('POLYGON((-10 0, -10 -10, 0 -10, 10 10, 0 10, 10 10, 0 10, -10 10, -10 0))'));

INSERT INTO Maps_Users(username, map_id) VALUES('Mohammed',001);
INSERT INTO Maps_Users(username, map_id) VALUES('Rami',001);

INSERT INTO Shapes(shape_creater, map_id, icon, shape_type, center, area_or_path, title, description, rate) 
VALUES('Mohammed',001,'icon_url_or_image','Point',POINT(0,0),null, 'The center','The center of the earth cord. system',5);

INSERT INTO Shapes(shape_creater, map_id, icon, shape_type, center, area_or_path, title, description, rate) 
VALUES('Rami',001,'icon_url_or_image','Area',POINT(0,0),GEOMFROMTEXT('LineString(-10 -10,10 10,-10 10,-10 -10)'), 'An area','this is an area in the sea',5);

INSERT INTO Shapes(shape_creater, map_id, icon, shape_type, center, area_or_path, title, description, rate) 
VALUES('Rami',001,'icon_url_or_image','Path',POINT(0,0),GEOMFROMTEXT('LineString(-10 -10,0 0,10 10)'), 'NorthEAST Direction','Going north east',3);

SELECT * FROM Persons;
SELECT *, astext(geo_boundery) FROM Maps;
SELECT * FROM Maps_Users;
SELECT *, astext(center), astext(area_or_path) FROM Shapes;

SELECT * FROM Maps WHERE  INTERSECTS(geo_boundery, GEOMFROMTEXT('LineString(-10 -10,0 0,10 10)')) = 1;

SELECT * FROM Maps WHERE  intersects(geo_boundery, GEOMFROMTEXT('LineString(-11 -11,-20 -20,-30 -30)')) = 1;

SELECT * FROM Maps WHERE  MBRCONTAINS(geo_boundery, GEOMFROMTEXT('LineString(-9 -9,-20 -20,-30 -30)')) = 1;

SELECT * FROM Maps WHERE  INTERSECTS(geo_boundery, GEOMFROMTEXT('LineString(-9 -9,-20 -20,-30 -30)')) = 1;
