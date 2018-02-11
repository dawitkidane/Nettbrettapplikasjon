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
def hello_world():
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
    return render_template('home.html')

@app.route('/login', methods=['POST','GET'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db()
    cursor = conn.cursor()
    sql = "SELECT COUNT(username) FROM Persons WHERE username = %s AND login_pass = %s LIMIT 0, 1;"
    try:
        cursor.execute(sql, (username, password))
        does_exist = cursor.fetchone()[0]

        if does_exist == 1:
            session["Logged_in"] = username
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
        sql = "INSERT INTO Maps(map_creater, title, description, end_date, geo_boundery)" \
              "VALUES(%s,%s,%s,%s,"+geo_boundery+");"
        try:
            cursor.execute(sql, (map_creater,title,description,enddate))
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
                "creater": '',
                "title": '',
                "issuedate": '',
                "expirydate": ''
            }
            conn = get_db()
            cursor = conn.cursor()

            sql = "SELECT map_creater, title, start_date, end_date FROM Maps WHERE map_id = "+str(mapid)+";"
            try:
                cursor.execute(sql)
                data = cursor.fetchone()
                map['creater'] = data[0]
                map['title'] = data[1]
                map['issuedate'] = str(data[2])
                map['expirydate'] = str(data[3])

                maps.append(map)


            except mysql.connector.Error as err:
                conn.close()
                print(err.msg)

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
    finally:
        conn.close()

    return render_template("allmaps.html", maps=maps)


@app.route("/MapChoices", methods=['GET'])
def map_choices():
    mapid = request.args.get('mapid')
    username = session.get("Logged_in")

    return render_template("MapChoices.html", mapid=mapid)


@app.route("/ShowMap", methods=['GET'])
def show_map():
    mapid = request.args.get('mapid')
    username = session.get("Logged_in")

    ## TODO: check if the user have right to enter this map
    conn = get_db()
    cursor = conn.cursor()
    sql = "SELECT COUNT(*) from Maps_Users WHERE username = '"+str(username)+"' AND map_id = "+str(mapid)+" LIMIT 0, 1;"
    try:
        cursor.execute(sql)
        have_right = cursor.fetchone()[0]
        if have_right == 1:
            ## TODO: read map details from data base and return render template with results

            sql = "SELECT map_creater, title, description, start_date, end_date, astext(geo_boundery) " \
                  "FROM Maps " \
                  "WHERE map_id = "+str(mapid)+";"

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
                "northeastcorner": bounds[0].replace(" ",","),
                "southwestcorner": bounds[1].replace(" ",",")
            }

            sql = "SELECT shape_id, shape_creater, icon, shape_type, astext(center), astext(area_or_path), title, description, rate " \
                  "FROM Shapes WHERE map_id = "+str(mapid)+";"
            cursor.execute(sql)
            data = cursor.fetchall()
            shapes = []
            for entry in data:
                shape = {
                    "shapeid": entry[0],
                    "shapecreater": entry[1],
                    "icon": entry[2],
                    "shapetype": entry[3],
                    "center": str(entry[4]).strip('POINT').replace(" ",", "),
                    "areaorpath": str(entry[5]).strip("LINESTRING").strip("(").strip(")"),
                    "title": entry[6],
                    "description": entry[7],
                    "rate": entry[8]
                }
                shapes.append(shape)

        else:
            return render_template("ViewMap.html", map={}, shapes=[], Fail="Du har ingen tilgang til dette kartet, kontakt administrator")

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return render_template("ViewMap.html", map={}, shapes=[], Fail=err.msg)
    finally:
        conn.close()
        return render_template("ViewMap.html", map=map, shapes=shapes)

@app.route("/AddPointToMap", methods=['GET'])
def add_point_to_map():
    mapid = request.args.get('mapid')
    username = session.get("Logged_in")
    if request.method == 'GET':
        ## TODO: check if the user have right to enter this map
        conn = get_db()
        cursor = conn.cursor()
        sql = "SELECT COUNT(*) from Maps_Users WHERE username = '" + str(username) + "' AND map_id = " + str(
            mapid) + " LIMIT 0, 1;"
        try:
            cursor.execute(sql)
            have_right = cursor.fetchone()[0]
            if have_right == 1:
                ## TODO: read map details from data base and return render template with results

                sql = "SELECT map_creater, title, description, start_date, end_date, astext(geo_boundery) " \
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
                    "northeastcorner": bounds[0].replace(" ", ","),
                    "southwestcorner": bounds[1].replace(" ", ",")
                }

                sql = "SELECT shape_id, shape_creater, icon, shape_type, astext(center), astext(area_or_path), title, description, rate " \
                      "FROM Shapes WHERE map_id = " + str(mapid) + ";"
                cursor.execute(sql)
                data = cursor.fetchall()
                shapes = []
                for entry in data:
                    shape = {
                        "shapeid": entry[0],
                        "shapecreater": entry[1],
                        "icon": entry[2],
                        "shapetype": entry[3],
                        "center": str(entry[4]).strip('POINT').replace(" ", ", "),
                        "areaorpath": str(entry[5]).strip("LINESTRING").strip("(").strip(")"),
                        "title": entry[6],
                        "description": entry[7],
                        "rate": entry[8]
                    }
                    shapes.append(shape)

            else:
                return render_template("AddPointToMap.html", map={}, shapes=[],
                                       Fail="Du har ingen tilgang til dette kartet, kontakt administrator")

        except mysql.connector.Error as err:
            conn.close()
            print(err.msg)
            return render_template("AddPointToMap.html", map={}, shapes=[], Fail=err.msg)
        finally:
            conn.close()
            return render_template("AddPointToMap.html", map=map, shapes=shapes)

@app.route("/AddRoadOrAreaToMap", methods=['GET'])
def add_road_or_area_to_map():
    mapid = request.args.get('mapid')
    username = session.get("Logged_in")

    if request.method == 'GET':
        ## TODO: check if the user have right to enter this map
        conn = get_db()
        cursor = conn.cursor()
        sql = "SELECT COUNT(*) from Maps_Users WHERE username = '" + str(username) + "' AND map_id = " + str(
            mapid) + " LIMIT 0, 1;"
        try:
            cursor.execute(sql)
            have_right = cursor.fetchone()[0]
            if have_right == 1:
                ## TODO: read map details from data base and return render template with results

                sql = "SELECT map_creater, title, description, start_date, end_date, astext(geo_boundery) " \
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
                    "northeastcorner": bounds[0].replace(" ", ","),
                    "southwestcorner": bounds[1].replace(" ", ",")
                }

                sql = "SELECT shape_id, shape_creater, icon, shape_type, astext(center), astext(area_or_path), title, description, rate " \
                      "FROM Shapes WHERE map_id = " + str(mapid) + ";"
                cursor.execute(sql)
                data = cursor.fetchall()
                shapes = []
                for entry in data:
                    shape = {
                        "shapeid": entry[0],
                        "shapecreater": entry[1],
                        "icon": entry[2],
                        "shapetype": entry[3],
                        "center": str(entry[4]).strip('POINT').replace(" ", ", "),
                        "areaorpath": str(entry[5]).strip("LINESTRING").strip("(").strip(")"),
                        "title": entry[6],
                        "description": entry[7],
                        "rate": entry[8]
                    }
                    shapes.append(shape)

            else:
                return render_template("AddRoadOrAreaToMap.html", map={}, shapes=[],
                                       Fail="Du har ingen tilgang til dette kartet, kontakt administrator")

        except mysql.connector.Error as err:
            conn.close()
            print(err.msg)
            return render_template("AddRoadOrAreaToMap.html", map={}, shapes=[], Fail=err.msg)
        finally:
            conn.close()
            return render_template("AddRoadOrAreaToMap.html", map=map, shapes=shapes)

@app.route("/registerShape", methods=['POST'])
def registerShape():
    username = session.get('Logged_in')
    map_id = request.form.get("map_id")
    icon = request.form.get("icon")
    shape_type = request.form.get("shape_type")
    center = "POINT"+request.form.get("center")
    area_or_path = "GEOMFROMTEXT('LineString("+request.form.get("area_or_path")+")')"
    title = request.form.get("title")
    description = request.form.get("description")
    rating = request.form.get("rating")

    conn = get_db()
    cursor = conn.cursor()
    sql = "INSERT INTO Shapes(shape_creater, map_id, icon, shape_type, center, area_or_path, title, description, rate) " \
          "VALUES(%s,%s,%s,%s,"+center+","+area_or_path+",%s,%s,%s);"
    try:
        cursor.execute(sql, (username, map_id, 'icon_url_or_image', shape_type, title, description, rating))
        conn.commit()
    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return "Failed"
    finally:
        conn.close()

    return "OK"



if __name__ == '__main__':
    app.run()