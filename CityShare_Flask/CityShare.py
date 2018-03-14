from flask import Flask, render_template, url_for, request, json, g, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "any random string"

def get_db():
    if not hasattr(g,'_database'):
        g._database = mysql.connector.connect(host='sql2.freemysqlhosting.net',
                                                user='sql2217838',
                                                passwd='cR3!bC4!',
                                                db='sql2217838')
    return g._database

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/signup', methods=['POST','GET'])
def signup():

    if request.method == 'GET':
        return render_template("signup.html")
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        surname = request.form.get('surname')
        email = request.form.get('email')
        telephone = request.form.get('telephone')

        conn = get_db()
        cursor = conn.cursor()
        sql = "INSERT INTO Persons(username, login_pass, first_name, last_name, e_post, telephone) " \
              "VALUES(%s,%s,%s,%s,%s,%s);"
        try:
            cursor.execute(sql, (username,password,firstname,surname,email,telephone))
            conn.commit()
            session["Logged_in"] = username
            return render_template("home.html")

        except mysql.connector.Error as err:
            conn.close()
            if err.msg == "Duplicate entry '"+username+"' for key 'PRIMARY'":
                return render_template("signup.html", fail=True, msg="Brukernavn er allerede tatt, prøv en annen!")
        finally:
            conn.close()

    return render_template("signup.html", fail=True, msg='Noe gikk galt, prøv igjen!')

@app.route('/signout')
def signout():
    session.pop('Logged_in', None)
    session.pop('is_Admin', None)
    return render_template('home.html')

@app.route('/login', methods=['POST','GET'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db()
    cursor = conn.cursor()
    sql = "SELECT COUNT(username), is_admin FROM Persons WHERE BINARY username = %s AND BINARY login_pass = %s LIMIT 0, 1;"
    try:
        cursor.execute(sql, (username, password))
        row = cursor.fetchone()
        does_exist = row[0]
        is_admin = row[1] #cursor.fetchone()[1]

        if does_exist == 1:
            session["Logged_in"] = username

            if is_admin == 1:
                session["is_Admin"] = is_admin

            return render_template("home.html")
        else:
            session["Logged_in"] = "Feil brukernavn eller passord"

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        session['Logged_in'] = "Database feil"
    finally:
        conn.close()

    return render_template("home.html")

@app.route("/searchUsers", methods=['POST'])
def search_for_users():
    username = request.form.get('username')
    ### TODO: search in database and return results
    conn = get_db()
    cursor = conn.cursor()
    sql = "SELECT username FROM Persons where username = 'search';".replace('search', username)
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        users = []
        for entry in data:
            users.append(entry)
    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
    finally:
        conn.close()

    return json.dumps(users)

@app.route('/addnewmap', methods=['POST','GET'])
def add_new_map():

    if request.method == 'GET':
        return render_template("new_map.html")

    else:
        map_creater = session.get("Logged_in")
        title = request.form.get('title')
        description = request.form.get('description')

        date = request.form.get('date')
        enddate = date[6:] + "-" + date[0:2] + "-" + date[3:5]

        geo_boundery = request.form.get('geo_boundery')
        geo_boundery = geo_boundery.replace("((","")
        geo_boundery = geo_boundery.replace(")","")
        geo_boundery = geo_boundery.replace("(", "")
        geo_boundery = geo_boundery.replace(",","")
        array = geo_boundery.split(" ")
        a = str(array[0])
        b = str(array[1])
        c = str(array[2])
        d = str(array[3])
        geo_boundery = "GEOMFROMTEXT('POLYGON(("+a+" "+b+", "+c+" "+d+", "+a+" "+b+"))')"

        geo_zoom = request.form.get('geo_zoom')

        users = request.form.getlist('users')
        if map_creater not in users:
            users.append(map_creater)

        points_categories = request.form.getlist('point_categories')
        roads_categories = request.form.getlist('road_categories')
        areas_categories = request.form.getlist('area_categories')
        """
        ['asdasd,Point,2hand.png', 'zoo,Point,zoo.png']
        ['black,Road,#000000', 'blue,Road,#0000ff', 'green,Road,#008000']
        ['red,Area,#ff0000', 'white,Area,#ffffff', 'yellow,Area,#ffff00', 'purple,Area,#e916d9']
        
        """

        ## TODO: ADD MAP TO DATABASE, 2 TABLES USERS AND MAPS
        conn = get_db()
        cursor = conn.cursor()
        sql = "INSERT INTO Maps(map_creater, title, description, end_date, geo_boundery, zoom)" \
              "VALUES(%s,%s,%s,%s,"+geo_boundery+",%s);"
        try:
            cursor.execute(sql, (map_creater,title,description,enddate,geo_zoom))
            conn.commit()
            Map_id = cursor.lastrowid

        except mysql.connector.Error as err:
            conn.close()
            print(err.msg)
            return render_template("new_map.html")

        ## TODO: adding users to the map
        cursor = conn.cursor()
        try:
            for user in users:
                sql = "INSERT INTO Maps_Users(username, map_id) VALUES(%s,%s);"
                cursor.execute(sql, (user, Map_id))
                conn.commit()
        except mysql.connector.Error as err:
            print(err.msg)

        cursor = conn.cursor()
        try:
            categories = points_categories + roads_categories + areas_categories
            for category in categories:
                cat = category.split(',')
                sql = "INSERT INTO Maps_Categories(category_name, category_type, category_image_or_color, map_id) " \
                      "VALUES(%s,%s,%s,%s);"
                cursor.execute(sql, (cat[0], cat[1], cat[2], Map_id))
                conn.commit()
        except mysql.connector.Error as err:
            conn.close()
            print(err.msg)
        finally:
            conn.close()
            return render_template("home.html")

        return render_template("new_map.html")

@app.route("/showmaps", methods=['GET'])
def show_maps():
    username = session.get("Logged_in")
    conn = get_db()
    cursor = conn.cursor()
    sql= "SELECT map_id FROM Maps_Users WHERE username = '"+username+"';"
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        mapids = []
        for entry in data:
            mapids.append(entry[0])

        maps = []
        for mapid in mapids:
            map = {
                "mapid": mapid,
            }
            conn = get_db()
            cursor = conn.cursor()

            sql = "SELECT map_creater, title, date(start_date), end_date, description, astext(Centroid(geo_boundery)), zoom FROM Maps WHERE map_id = "+str(mapid)+";"
            try:
                cursor.execute(sql)
                data = cursor.fetchone()
                map['creater'] = data[0]
                map['title'] = data[1]
                map['issuedate'] = str(data[2])
                map['expirydate'] = str(data[3])
                map['description'] = str(data[4])
                map['center'] = (str(data[5]).strip("POINT(").strip(")")).replace(" ",",")
                map['zoom'] = str(data[6])

                maps.append(map)


            except mysql.connector.Error as err:
                conn.close()
                print(err.msg)

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
    finally:
        conn.close()

    return render_template("view_maps.html", maps=maps)

@app.route("/EditMap", methods=['GET'])
def edit_map():
    mapid = request.args.get('mapid')
    username = session.get("Logged_in")

    ## TODO: check if the user have right to enter this map
    conn = get_db()
    cursor = conn.cursor()
    sql = "SELECT COUNT(*) from Maps_Users WHERE username = '" + str(username) + "' AND map_id = " + str(
        mapid) + " LIMIT 0, 1;"
    try:
        cursor.execute(sql)
        have_right = cursor.fetchone()[0]
        if have_right == 1:

            ## Reading map details from database and return render template with results
            sql = "SELECT map_creater, title, description, start_date, end_date, astext(geo_boundery), zoom " \
                  "FROM Maps " \
                  "WHERE map_id = " + str(mapid) + ";"
            cursor.execute(sql)
            data = cursor.fetchone()
            bounds = str(data[5]).strip("POLYGON((").strip("))").split(",")
            map = {
                "mapid": mapid,
                "creater": data[0],
                "title": data[1],
                "description": data[2],
                "issuedate": data[3],
                "expirydate": data[4],
                "bounds": bounds,
                "zoom": data[6],
                "northeastcorner": bounds[0].replace(" ", ","),
                "southwestcorner": bounds[1].replace(" ", ","),
                "map_users": [],
                "logged_in_user": str(username)
            }
            sql = "SELECT username FROM Maps_Users WHERE map_id = "+str(mapid)+";"
            cursor.execute(sql)
            data = cursor.fetchall();
            for username in data:
                map["map_users"].append(username[0]);


            ## Reading already registered shapes on map
            sql = "SELECT S.shape_id, S.shape_creater, astext(S.center), astext(S.area_or_path), S.title, S.description, " \
                  "S.rate, M.category_type, M.category_image_or_color " \
                  "FROM Shapes S JOIN Maps_Categories M " \
                  "ON S.category_ID = M.category_ID " \
                  "WHERE map_id = MAP_ID;".replace("MAP_ID", str(mapid))
            cursor.execute(sql)
            data = cursor.fetchall()
            points = []
            roads = []
            areas = []
            for entry in data:
                shape = {
                    "shape_id": entry[0],
                    "shape_creater": entry[1],
                    "shape_center": str(entry[2]).strip('POINT').replace(" ", ", "),
                    "area_or_path": str(entry[3]).strip("LINESTRING").strip("(").strip(")"),
                    "title": entry[4],
                    "description": str((entry[5])).replace("\n","{n}"),
                    "rating": entry[6],
                    "category_type": entry[7],
                    "icon": entry[8]
                }

                if shape['shape_creater'] == username or session.get("is_Admin") == 1:
                    if shape['category_type'] == "Point":
                        points.append(shape)
                    elif shape['category_type'] == "Road":
                        roads.append(shape)
                    elif shape['category_type'] == "Area":
                        areas.append(shape)

            ## Reading registered Categories
            sql = "SELECT category_ID, category_name, category_type, category_image_or_color FROM Maps_Categories WHERE map_id = "+str(mapid)+";"
            cursor.execute(sql)
            data = cursor.fetchall()
            points_categories = []
            areas_categories = []
            roads_categories = []
            for entry in data:
                category = {
                    "ID": entry[0],
                    "name": entry[1],
                    "type": entry[2],
                    "image_or_color": entry[3]
                }
                if category["type"] == "Point":
                    points_categories.append(category)
                elif category["type"] == "Road":
                    roads_categories.append(category)
                elif category["type"] == "Area":
                    areas_categories.append(category)



        else:
            return render_template("edit_map.html", map={}, points=[], roads=[], area=[],
                                   Fail="Du har ingen tilgang til dette kartet, kontakt administrator")

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return render_template("edit_map.html", map={}, shapes=[], Fail=err.msg)
    finally:
        conn.close()
        return render_template("edit_map.html", map=map, points_categories=points_categories, roads_categories=roads_categories,
                               areas_categories=areas_categories, points=points, roads=roads, area=areas)

    return render_template("edit_map.html", mapid=mapid)

@app.route("/registerShape", methods=['POST'])
def registerShape():

    username = session.get('Logged_in')
    category_id = request.form.get("categoryID")
    center = "POINT"+request.form.get("center")
    area_or_path = request.form.get("area_or_path")
    title = request.form.get("title")
    description = request.form.get("description")
    rating = request.form.get("rating")

    conn = get_db()
    cursor = conn.cursor()

    sql = ""
    if area_or_path is None:
        sql = "INSERT INTO Shapes(category_ID, shape_creater, center, title, description, rate)" \
              "VALUES(%s,%s," + center + ",%s,%s,%s);"
    else:
        area_or_path_coordinates = "geomfromtext('LINESTRING("+request.form.get("area_or_path")+")')"
        sql = "INSERT INTO Shapes(category_ID, shape_creater, center, area_or_path, title, description, rate)" \
              "VALUES(%s,%s," + center + "," + area_or_path_coordinates + ",%s,%s,%s);"

    try:
        cursor.execute(sql, (category_id, username, title, description, rating))
        Shape_id = cursor.lastrowid
        conn.commit()
    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return "Failed"
    finally:
        conn.close()

    return str(Shape_id)

@app.route("/updateShape", methods=['POST'])
def updateShape():
    username = session.get('Logged_in')

    shape_id = request.form.get('shape_id')
    title = request.form.get("title")
    description = request.form.get("description")
    rating = request.form.get("rating")

    conn = get_db()
    cursor = conn.cursor()
    sql = "UPDATE Shapes " \
          "SET title = '"+title+"', description = '"+description+"', rate = "+str(rating)+" " \
          "WHERE shape_id = "+str(shape_id)+";"
    try:
        cursor.execute(sql)
        conn.commit()
    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return "Failed"
    finally:
        conn.close()

    return "OK"

@app.route("/deleteShape", methods=['POST'])
def deleteShape():
    shape_id = request.form.get('shape_id')

    conn = get_db()
    cursor = conn.cursor()
    sql = "DELETE FROM Shapes WHERE shape_id = ID;".replace("ID", shape_id);
    try:
        cursor.execute(sql)
        conn.commit()
    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return "Failed"
    finally:
        conn.close()

    return "Deleted"

if __name__ == '__main__':
    app.run()