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
category_name VARCHAR(30),
category_type VARCHAR(30),
category_image_or_color VARCHAR(30),
map_id INT,
PRIMARY KEY (category_name, category_type, category_image_or_color, map_id),
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
VALUES('Dawit','Dawit1995','Dawit','Kidane','d_kzzz@yahoo.com',0047450088910,TRUE);

INSERT INTO Persons(username, login_pass, first_name, last_name, e_post, telephone) 
VALUES('Rami','Rami1992','Rami','Guniem','rami@yahoo.no',004777665544);

/*
INSERT INTO Maps(map_creater, title, description, end_date, geo_boundery) 
VALUES('Mohammed','My map title','my map description','2018-05-15',GEOMFROMTEXT('POLYGON((-10 0, -10 -10, 0 -10, 10 10, 0 10, 10 10, 0 10, -10 10, -10 0))'));


INSERT INTO Maps(map_creater, title, description, end_date, geo_boundery) 
VALUES('Mohammed','My map title','my map description','2018-05-15',GEOMFROMTEXT('POLYGON((51.42318883058882 -0.3079609008789248, 51.594134820664564 -0.3079609008789248, 51.42318883058882 -0.3079609008789248))'));


INSERT INTO Maps_Users(username, map_id) VALUES('Mohammed',001);
INSERT INTO Maps_Users(username, map_id) VALUES('Rami',001);

INSERT INTO Shapes(shape_creater, map_id, icon, shape_type, center, area_or_path, title, description, rate) 
VALUES('Mohammed',001,'icon_url_or_image','Point', GEOMFROMTEXT('POINT(0,0)'),NULL, 'The center','The center of the earth cord. system',5);

INSERT INTO Shapes(shape_creater, map_id, icon, shape_type, center, area_or_path, title, description, rate) 
VALUES('Rami',001,'icon_url_or_image','Area',POINT(0,0),GEOMFROMTEXT('LineString(-10 -10,10 10,-10 10,-10 -10)'), 'An area','this is an area in the sea',5);

INSERT INTO Shapes(shape_creater, map_id, icon, shape_type, center, area_or_path, title, description, rate) 
VALUES('Rami',001,'icon_url_or_image','Path',POINT(0,0),GEOMFROMTEXT('LineString(-10 -10,0 0,10 10)'), 'NorthEAST Direction','Going north east',3);
*/

/*
INSERT INTO Shapes(shape_creater, map_id, icon, shape_type, center, area_or_path, title, description, rate) 
VALUES('Mohammed',001,'icon_url_or_image','Point', POINT(41,11),NULL, 'east','The center of the earth cord. system',5);
INSERT INTO Shapes(shape_creater, map_id, icon, shape_type, center, area_or_path, title, description, rate) 
VALUES('Mohammed',001,'icon_url_or_image','Point', POINT(42,14),NULL, 'west','The center of the earth cord. system',5);
INSERT INTO Shapes(shape_creater, map_id, icon, shape_type, center, area_or_path, title, description, rate) 
VALUES('Mohammed',001,'icon_url_or_image','Point', POINT(43,11),NULL, 'north','The center of the earth cord. system',5);
INSERT INTO Shapes(shape_creater, map_id, icon, shape_type, center, area_or_path, title, description, rate) 
VALUES('Mohammed',001,'icon_url_or_image','Point', POINT(41,14),NULL, 'south','The center of the earth cord. system',5);
INSERT INTO Shapes(shape_creater, map_id, icon, shape_type, center, area_or_path, title, description, rate) 
VALUES('Mohammed',001,'icon_url_or_image','Area',POINT(41.75,12.5),GEOMFROMTEXT('LineString(41 11,42 14,43 11,41 14,41 11)'), 'An area','this is an area in italy',5);
INSERT INTO Shapes(shape_creater, map_id, icon, shape_type, center, area_or_path, title, description, rate) 
VALUES('Mohammed',001,'icon_url_or_image','Road',POINT(35,10),GEOMFROMTEXT('LineString(35 0,35 5,35 10,35 15,25 20)'), 'A Road','this is an area in italy',5);


SELECT * FROM Persons;
SELECT *, astext(geo_boundery) FROM Maps;
SELECT * FROM Maps_Users;
SELECT shape_id, shape_creater, map_id, icon, shape_type, astext(center), astext(area_or_path), title, description, rate FROM Shapes;
SELECT astext(center), astext(area_or_path)FROM Shapes WHERE map_id = 001;

SELECT * FROM Maps WHERE  INTERSECTS(geo_boundery, GEOMFROMTEXT('LineString(-10 -10,0 0,10 10)')) = 1;
SELECT * FROM Maps WHERE  intersects(geo_boundery, GEOMFROMTEXT('LineString(-11 -11,-20 -20,-30 -30)')) = 1;
SELECT * FROM Maps WHERE  MBRCONTAINS(geo_boundery, GEOMFROMTEXT('LineString(-9 -9,-20 -20,-30 -30)')) = 1;
SELECT * FROM Maps WHERE  INTERSECTS(geo_boundery, GEOMFROMTEXT('LineString(-9 -9,-20 -20,-30 -30)')) = 1;


SELECT shape_id, shape_creater, icon, shape_type, astext(center), astext(area_or_path), title, description, rate FROM Shapes WHERE map_id = 2


INSERT INTO Maps_Categories(category_name, category_type, category_image_or_color, map_id) 
VALUES('black','Road','#000000', 001);


select * from Maps_Categories;
select * from Maps_Users;

SELECT * FROM Maps_Categories WHERE category_type = 'POINT' AND map_id = 10; 
SELECT * FROM Maps_Categories WHERE category_type = 'Road' AND map_id = 10; 
SELECT * FROM Maps_Categories WHERE category_type = 'Area' AND map_id = 10;
*/