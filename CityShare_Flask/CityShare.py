from flask import Flask, render_template, url_for, request, json, g, session, redirect
import mysql.connector
import Classes

app = Flask(__name__)
app.secret_key = "any random string"

def get_db():
    if not hasattr(g, '_database'):
        g._database = mysql.connector.connect(host='sql2.freemysqlhosting.net',
                                              user='sql2217838',
                                              passwd='cR3!bC4!',
                                              db='sql2217838')
    return g._database

"""
def get_db():
    if not hasattr(g, '_database'):
        g._database = mysql.connector.connect(host='mysql2.ux.uis.no',
                                              user='mguniem',
                                              passwd='8jtmyytk',
                                              db='dbmguniem')
    return g._database
"""

@app.route('/')
def index():
    return render_template("home.html")


@app.route('/signup', methods=['POST', 'GET'])
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
              "VALUES(aes_encrypt(%s,'enckey'),aes_encrypt(%s,'enckey')," \
              "%s,%s,%s,%s);"
        try:
            cursor.execute(sql, (username, password, firstname, surname, email, telephone))
            conn.commit()
            session["Logged_in"] = username
            return render_template("home.html")

        except mysql.connector.Error as err:
            conn.close()
            if err.msg == "Duplicate entry '" + username + "' for key 'PRIMARY'":
                return render_template("signup.html", fail=True, msg="Brukernavn er allerede tatt, prov en annen!")
        finally:
            conn.close()

    return render_template("signup.html", fail=True, msg='Noe gikk galt, prov igjen!')


@app.route('/Update_Account', methods=['POST', 'GET'])
def update_account():
    username = session.get('Logged_in', None)
    if username is None:
        return render_template("error.html", msg="Du ma vaere innlogget for a apne din konto !")

    try:
        conn = get_db()
        cursor = conn.cursor()
        if request.method == 'GET':
            sql = "SELECT cast(aes_decrypt(login_pass, 'enckey') AS CHAR(20)), first_name, last_name, e_post, telephone " \
                  "FROM Persons " \
                  "WHERE username = aes_encrypt('USERNAME','enckey')".replace('USERNAME', username)
            cursor.execute(sql)
            data = cursor.fetchone()
            person = {
                "username": username,
                "pass": data[0],
                "first_name": data[1],
                "last_name": data[2],
                "e_post": data[3],
                "tele": data[4]
            }
            return render_template("update_account.html", person=person)
        else:
            sql = "UPDATE Persons " \
                  "SET login_pass = aes_encrypt('PASS','enckey'), first_name = 'FIRST_NAME', " \
                  "last_name = 'LAST_NAME', e_post = 'MAIL', telephone = 'TELE' " \
                  "WHERE username = aes_encrypt('USERNAME','enckey');".replace('USERNAME', username)
            sql = sql.replace("PASS", request.form.get("password"))
            sql = sql.replace("FIRST_NAME", request.form.get("firstname"))
            sql = sql.replace("LAST_NAME", request.form.get("surname"))
            sql = sql.replace("MAIL", request.form.get("email"))
            sql = sql.replace("TELE", request.form.get("telephone"))
            cursor.execute(sql)
            conn.commit()
            return redirect("/")

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return redirect("/")


@app.route('/signout')
def signout():
    session.pop('Logged_in', None)
    return render_template('home.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db()
    cursor = conn.cursor()
    sql = "SELECT count(username) " \
          "FROM Persons " \
          "WHERE BINARY username = aes_encrypt(%s,'enckey') AND BINARY login_pass = aes_encrypt(%s,'enckey') " \
          "LIMIT 0, 1;"
    try:
        cursor.execute(sql, (username, password))
        row = cursor.fetchone()
        does_exist = row[0]

        if does_exist == 1:
            session["Logged_in"] = username
            return render_template("home.html")

        else:
            Error = "Feil brukernavn eller passord"

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        Error = "Database feil"
    finally:
        conn.close()

    return render_template("home.html", Error=Error)


@app.route("/searchUsers", methods=['POST'])
def search_for_users():
    username = request.form.get('username')
    ### TODO: search in database and return results
    conn = get_db()
    cursor = conn.cursor()
    #sql = "SELECT username FROM Persons where username = 'search' or e_post = 'search';".replace('search', username)
    sql = "SELECT cast(aes_decrypt(username, 'enckey') AS CHAR(20)) " \
          "FROM Persons where username = aes_encrypt('search','enckey') or e_post = 'search';".replace('search', username)
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


@app.route('/addnewmap', methods=['POST', 'GET'])
def add_new_map():
    map_creater = session.get("Logged_in", None)

    authority = Classes.Authority(map_creater)

    if authority.is_logged_in() is False:
        return render_template("error.html", Fail_Code=4)

    if request.method == 'GET':
        return render_template("new_map.html")

    else:

        title = request.form.get('title')
        description = request.form.get('description')
        date = request.form.get('date')
        enddate = date[6:] + "-" + date[0:2] + "-" + date[3:5]

        geo_boundery = request.form.get('geo_boundery')
        geo_boundery = geo_boundery.replace("((", "")
        geo_boundery = geo_boundery.replace(")", "")
        geo_boundery = geo_boundery.replace("(", "")
        geo_boundery = geo_boundery.replace(",", "")
        array = geo_boundery.split(" ")
        a = str(array[0])
        b = str(array[1])
        c = str(array[2])
        d = str(array[3])
        geo_boundery = "GEOMFROMTEXT('POLYGON((" + a + " " + b + ", " + c + " " + d + ", " + a + " " + b + "))')"

        geo_zoom = request.form.get('geo_zoom')

        Interviewers = request.form.getlist('Interviewers')
        Administrators = request.form.getlist('Administrators')
        if map_creater not in Administrators:
            Administrators.append(map_creater)

        points_categories = request.form.getlist('point_categories')
        roads_categories = request.form.getlist('road_categories')
        areas_categories = request.form.getlist('area_categories')
        questions = request.form.getlist('questions')
        """
        ['asdasd,Point,2hand.png', 'zoo,Point,zoo.png']
        ['black,Road,#000000', 'blue,Road,#0000ff', 'green,Road,#008000']
        ['red,Area,#ff0000', 'white,Area,#ffffff', 'yellow,Area,#ffff00', 'purple,Area,#e916d9']
        ['How old are you ?', 'Where do you live ?']
        """

        ## TODO: ADD MAP TO DATABASE, 2 TABLES USERS AND MAPS
        conn = get_db()
        cursor = conn.cursor()
        sql = "INSERT INTO Maps(map_creater, title, description, end_date, geo_boundery, zoom)" \
              "VALUES(aes_encrypt(%s,'enckey'),%s,%s,%s," + geo_boundery + ",%s);"
        try:
            cursor.execute(sql, (map_creater, title, description, enddate, geo_zoom))
            conn.commit()
            Map_id = cursor.lastrowid

            for user in Interviewers:
                sql = "INSERT INTO Maps_Interviewers(username, map_id) VALUES(aes_encrypt(%s,'enckey'),%s);"
                cursor.execute(sql, (user, Map_id))
                conn.commit()

            for user in Administrators:
                sql = "INSERT INTO Maps_Administrators(username, map_id) VALUES(aes_encrypt(%s,'enckey'),%s);"
                cursor.execute(sql, (user, Map_id))
                conn.commit()

            categories = points_categories + roads_categories + areas_categories
            for category in categories:
                cat = category.split(',')
                sql = "INSERT INTO Maps_Categories(category_name, category_type, category_image_or_color, map_id) " \
                      "VALUES(%s,%s,%s,%s);"
                cursor.execute(sql, (cat[0], cat[1], cat[2], Map_id))
                conn.commit()

            for question in questions:
                sql = "INSERT INTO Maps_Questions(question, map_id) values(%s,%s);"
                cursor.execute(sql, (question, Map_id))
                conn.commit()


        except mysql.connector.Error as err:
            conn.close()
            print(err.msg)
            return render_template("new_map.html", Fail_Code=1)

        except Exception as err:
            conn.close()
            print(err)
            return render_template("new_map.html", Fail_Code=0)

        conn.close()
        return render_template("home.html")


@app.route("/showmaps", methods=['GET'])
def show_maps():
    username = session.get("Logged_in", None)

    authority = Classes.Authority(username)

    if authority.is_logged_in() is False:
        return render_template("error.html", Fail_Code=4)

    try:
        conn = get_db()
        cursor = conn.cursor()
        sql = "(SELECT map_id FROM Maps_Interviewers WHERE username = aes_encrypt('person','enckey'))" \
              "UNION ALL" \
              "(SELECT map_id FROM Maps_Administrators WHERE username = aes_encrypt('person','enckey'));".replace('person', str(username))

        cursor.execute(sql)
        data = cursor.fetchall()
        mapids = []
        for entry in set(data):
            mapids.append(entry[0])

        maps = []
        for mapid in mapids:
            map = {
                "mapid": mapid,
            }
            conn = get_db()
            cursor = conn.cursor()

            sql = "SELECT cast(aes_decrypt(map_creater, 'enckey') AS CHAR(20)), title, date(start_date), end_date, description, astext(Centroid(geo_boundery)), zoom FROM Maps WHERE map_id = " + str(
                mapid) + ";"

            cursor.execute(sql)
            data = cursor.fetchone()
            map['creater'] = data[0]
            map['title'] = data[1]
            map['issuedate'] = str(data[2])
            map['expirydate'] = str(data[3])
            map['description'] = str(data[4])
            map['center'] = (str(data[5]).strip("POINT(").strip(")")).replace(" ", ",")
            map['zoom'] = str(data[6])


            if username == map['creater']:
                map['Can_Update_Map'] = True

            maps.append(map)

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return render_template("error.html", Fail_Code=1)

    except Exception as err:
        conn.close()
        print(err)
        return render_template("error.html", Fail_Code=0)

    conn.close()
    return render_template("view_user_maps.html", maps=maps)


@app.route("/EditMap", methods=['GET'])
def edit_map():
    mapid = request.args.get('mapid')
    username = session.get("Logged_in", None)

    authority = Classes.Authority(username)

    if authority.is_logged_in() is False:
        return render_template("error.html", Fail_Code=4)

    is_valid = authority.is_map_valid(mapid)
    if type(is_valid) == int:
        return render_template("error.html", Fail_Code=is_valid)

    # get all users for this map
    Users = authority.get_map_users(mapid)
    if type(Users) == int:
        return render_template("error.html", Fail_Code=Users)

    try:
        conn = get_db()
        cursor = conn.cursor()

        # TODO: Reading map details from database
        sql = "SELECT cast(aes_decrypt(map_creater, 'enckey') AS CHAR(20)), title, description, start_date, end_date, astext(geo_boundery), zoom ,map_id " \
              "FROM Maps " \
              "WHERE map_id = MAP_ID;".replace("MAP_ID", str(mapid))

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
            "logged_in_user": str(username)
        }

        # TODO: Reading registered Categories
        sql = "SELECT category_ID, category_name, category_type, category_image_or_color FROM Maps_Categories WHERE map_id = " + str(
            mapid) + ";"
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

        # TODO: Reading registered Questions
        sql = "SELECT question_ID, question FROM Maps_Questions WHERE map_id = MAP_ID;".replace("MAP_ID", str(mapid))
        cursor.execute(sql)
        data = cursor.fetchall()
        questions = []
        for entry in data:
            question = {
                "ID": entry[0],
                "question": entry[1]
            }
            questions.append(question)

        conn.close()

        return render_template("open_map.html", map=map, points_categories=points_categories,
                               roads_categories=roads_categories, questions=questions,
                               areas_categories=areas_categories)

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return render_template("error.html", Fail_Code=1)

    except Exception as err:
        conn.close()
        print(err)
        return render_template("error.html", Fail_Code=0)


@app.route("/RegisterRespondoent", methods=['POST'])
def RegisterRespondoent():
    Respondoent = json.loads(request.form.get('Respondoent'))
    Shapes = json.loads(request.form.get('Shapes'))
    Map_id = request.form.get('Map_id')
    logged_in_user = session.get("Logged_in", None)


    authority = Classes.Authority(logged_in_user)
    if authority.is_logged_in() is False:
        return "4"

    all_users = authority.get_map_users(Map_id)

    if logged_in_user not in all_users:
        return "2"

    is_valid = authority.is_map_valid(Map_id)
    if type(is_valid) == int:
        return str(is_valid)

    # TODO Insert/create new respondent
    try:
        conn = get_db()
        cursor = conn.cursor()
        sql = "INSERT INTO Maps_Respondents(map_id) VALUES(Map_id);".replace("Map_id", str(Map_id))

        cursor.execute(sql)
        conn.commit()
        Respondoent_id = cursor.lastrowid

        # TODO Insert respondent's answers
        for key in Respondoent:
            question = dict(Respondoent[key])
            sql = "INSERT INTO Respondent_Answers(respondent_ID, question_ID, Answer) VALUES(%s,%s,%s);"
            cursor.execute(sql, (Respondoent_id, question["ID"], question["answer"]))
            conn.commit()

        # TODO Insert respondent's shapes
        for key in Shapes:
            shape = dict(Shapes[key])

            center = "POINT" + str(shape['center'])
            area_or_path = "geomfromtext('LINESTRING(" + str(shape['area_or_path']) + ")')"
            sql = "INSERT INTO Shapes(category_ID, shape_creater, center, area_or_path, title, description, rate, respondent_ID)" \
                  "VALUES(%s, aes_encrypt(%s,'enckey'), " + center + ", " + area_or_path + ", %s, %s, %s, %s);"

            cursor.execute(sql, (str(shape['category_ID']), str(logged_in_user), shape['title'],
                                 shape['description'], shape['rating'], str(Respondoent_id)))

        conn.commit()
        conn.close()
        return "Success"

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return "1"

    except Exception as err:
        conn.close()
        print(err)
        return "0"


@app.route("/ViewMapResult", methods=['GET'])
def view_map_result():
    mapid = request.args.get('mapid')
    username = session.get("Logged_in", None)

    authority = Classes.Authority(username)

    if authority.is_logged_in() is False:
        return render_template("error.html", Fail_Code=4)

    is_valid = authority.is_map_valid(mapid)
    if type(is_valid) == int:
        return render_template("error.html", Fail_Code=is_valid)

    # get all users for this map
    Users = authority.get_map_users(mapid)
    if type(Users) == int:
        return render_template("error.html", Fail_Code=Users)

    conn = get_db()
    cursor = conn.cursor()
    try:

        Interviewers, Administrators = authority.get_all_map_users(mapid)
        if type(Interviewers) == int:
            return render_template("error.html", Fail_Code=Interviewers)

        Administrators_names = []
        for user in Administrators:
            Administrators_names.append(user["username"])

        # TODO: Reading the map_details
        sql = "SELECT cast(aes_decrypt(map_creater, 'enckey') AS CHAR(20)), title, description, start_date, end_date, astext(geo_boundery), zoom ,map_id " \
              "FROM Maps " \
              "WHERE map_id = MAP_ID;".replace("MAP_ID", str(mapid))
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
            "logged_in_user": str(username)
        }

        # TODO: Reading registered Questions
        sql = "SELECT question_ID, question FROM Maps_Questions WHERE map_id = MAP_ID;".replace("MAP_ID", str(mapid))
        cursor.execute(sql)
        data = cursor.fetchall()
        questions = []
        for entry in data:
            question = {
                "question_ID": entry[0],
                "question": entry[1]
            }
            questions.append(question)

        # TODO: Reading registered responses including respondents, questions and respondent's answers
        sql = "SELECT A.respondent_ID, A.question_ID, A.Answer " \
              "FROM Respondent_Answers AS A JOIN Maps_Respondents AS R ON A.respondent_ID = R.respondent_ID " \
              "WHERE map_id = MAP_ID;".replace("MAP_ID", str(mapid))
        cursor.execute(sql)
        data = cursor.fetchall()
        questions_response = []
        for entry in data:
            Question_response = {
                "respondent_ID": entry[0],
                "question_ID": entry[1],
                "Answer": entry[2]
            }
            questions_response.append(Question_response)

        # TODO: Reading already registered shapes on map
        sql = "SELECT S.shape_id, cast(aes_decrypt(S.shape_creater, 'enckey') AS CHAR(20)), astext(S.center), astext(S.area_or_path), S.title, S.description, " \
              "S.rate, M.category_type, M.category_image_or_color, respondent_ID " \
              "FROM Shapes S JOIN Maps_Categories M ON S.category_ID = M.category_ID " \
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
                "description": str((entry[5])).replace("\n", "{n}"),
                "rating": entry[6],
                "category_type": entry[7],
                "icon": entry[8],
                "respondent_ID": entry[9]
            }

            if shape['shape_creater'] == username or username in Administrators_names:
                if shape['category_type'] == "Point":
                    points.append(shape)
                elif shape['category_type'] == "Road":
                    roads.append(shape)
                elif shape['category_type'] == "Area":
                    areas.append(shape)

        interviwers, administrators = authority.get_all_map_users(mapid)
        all_users = interviwers+administrators

        return render_template("analyze_map.html", Users=all_users, Map=map,
                               Questions=questions, Questions_response=questions_response,
                               Points=points, Areas=areas, Roads=roads)


    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return render_template("error.html", Fail_Code=1)

    except Exception as err:
        conn.close()
        print(err)
        return render_template("error.html", Fail_Code=0)

    conn.close()


@app.route("/Edit_Shape", methods=['POST'])
def edit_shape():
    map_id = request.form.get("map_id")
    username = session.get("Logged_in")
    Shape_id = request.form.get("shape_id")
    Task = request.form.get("task")

    authority = Classes.Authority(username)

    if authority.is_logged_in() is False:
        return "4"

    Interviewers, Administrators = authority.get_all_map_users(map_id)

    conn = get_db()
    cursor = conn.cursor()

    try:
        Interviewers_names = []
        for Interviewer in Interviewers:
            Interviewers_names.append(Interviewer["username"])

        Administrators_names = []
        for Administrator in Administrators:
            Administrators_names.append(Administrator["username"])

        if username not in Administrators_names and username not in Interviewers_names:
            return "2"

        ## TODO: Do the requested task to update
        if Task == "Update":
            Title = request.form.get("title")
            Description = request.form.get("description")
            Rating = request.form.get("rating")
            if username in Interviewers_names:
                sql = "UPDATE Shapes SET title = 'TITLE1', description = 'DESCRIPTION1', rate = 1 WHERE " \
                      "shape_creater = aes_encrypt('PERSON','enckey') " \
                      "AND shape_id = SHAPE_ID;".replace("SHAPE_ID", Shape_id).replace("PERSON", username)
            else:
                sql = "UPDATE Shapes " \
                      "SET title = 'TITLE', description = 'DESCRIPTION', rate = RATING " \
                      "WHERE shape_id = SHAPE_ID;".replace("SHAPE_ID", Shape_id)
            sql = sql.replace('TITLE', Title)
            sql = sql.replace('DESCRIPTION', Description)
            sql = sql.replace('RATING', Rating)
            cursor.execute(sql)
            conn.commit()
            conn.close()

            return "Success"

        ## TODO: Do the requested task to delete
        elif Task == "Delete":
            if username in Interviewers_names:
                sql = "DELETE FROM Shapes WHERE " \
                      "shape_creater = aes_encrypt('PERSON','enckey') " \
                      "AND shape_id = SHAPE_ID;".replace("SHAPE_ID", Shape_id).replace("PERSON", username)
            else:
                sql = "DELETE FROM Shapes " \
                      "WHERE shape_id = SHAPE_ID;".replace("SHAPE_ID", Shape_id)
            cursor.execute(sql)
            conn.commit()
            conn.close()

            return "Success"

        ## TODO: in case the task is not spesified
        else:
            conn.close()
            return "Unsupported Task"

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return "1"

    except Exception as err:
        conn.close()
        print(err)
        return "0"


@app.route("/DownloadMapAsCSVFile", methods=['POST'])
def download_map_as_csv_file():
    username = session.get("Logged_in")
    Map_id = json.loads(request.form.get('Map_id'))
    Shapes_data = json.loads(request.form.get('Data'))
    Respondents = json.loads(request.form.get("Respondoents"))

    authority = Classes.Authority(username)
    if authority.is_logged_in() is False:
        return "4"
    all_users = authority.get_map_users(str(Map_id))
    if type(all_users) == int:
        return str(all_users)

    conn = get_db()
    cursor = conn.cursor()

    try:
        file_header = "Map_ID,Map_bounds,Area_or_path_Coordinates,Center,Interviewer," \
                      "Title,Description,Rating,Category_type,Respondent_ID"

        sql = "SELECT question FROM Maps_Questions WHERE map_id = 'MAP_ID';".replace("MAP_ID", str(Map_id))
        cursor.execute(sql)
        questions = cursor.fetchall()
        for question in questions:
            file_header += "," + str(question[0])

        file_content = file_header + "\n"

        # TODO: Read map bounds
        sql = "SELECT astext(geo_boundery) FROM Maps WHERE map_id = 'MAP_ID';".replace("MAP_ID", str(Map_id))
        cursor.execute(sql)
        map_bounds = cursor.fetchone()[0]

        for shape_id in Shapes_data:
            line = str(Map_id)+","
            striped_bounds = (map_bounds.strip("POLYGON((")).strip("))")
            bounds_coordinates = striped_bounds.split(",")
            flipped_bounds = "POLYGON(("
            for coordinate in list(bounds_coordinates):
                flipped = coordinate.split(" ")
                flipped_bounds += flipped[1]+" "+flipped[0]+","
            flipped_bounds = flipped_bounds[:-1]+"))"
            line += flipped_bounds+","

            # TODO: Read relevant shape's data from database
            sql = "SELECT astext(S.area_or_path), astext(S.center), cast(aes_decrypt(S.shape_creater, 'enckey') AS CHAR(20)), S.title, S.description, " \
                  "S.rate, M.category_type, S.respondent_ID " \
                  "FROM Shapes S JOIN Maps_Categories M ON S.category_ID = M.category_ID " \
                  "WHERE map_id = 'MAP_ID' AND shape_id = 'SHAPE_ID';" \
                .replace("MAP_ID", str(Map_id)).replace("SHAPE_ID", str(shape_id))

            cursor.execute(sql)
            shape = cursor.fetchone()

            if str(shape[0]) != "None":
                striped_area_or_path = (str(shape[0]).strip("LINESTRING(")).strip(")")
                area_or_path_coordinates = striped_area_or_path.split(",")
                flipped_area_or_path = "LINESTRING("
                for coordinate in list(area_or_path_coordinates):
                    flipped = coordinate.split(" ")
                    flipped_area_or_path += flipped[1] + " " + flipped[0] + ","
                flipped_area_or_path = flipped_area_or_path[:-1] + ")"
                line += flipped_area_or_path + ","
            else:
                line += "None" + ","

            striped_center = (str(shape[1]).strip("POINT(")).strip(")")
            flipped_center = "POINT("
            flipped = striped_center.split(" ")
            flipped_center += flipped[1] + " " + flipped[0] + ")"
            line += flipped_center + ","


            line += str(shape[2])+","
            line += str(shape[3])+","
            line += str(shape[4])+","
            line += str(shape[5])+","
            line += str(shape[6])+","
            line += str(shape[7])+","

            sql = "SELECT Q.question, R.Answer " \
                  "FROM Respondent_Answers AS R JOIN Maps_Questions AS Q ON R.question_ID = Q.question_ID " \
                  "WHERE map_id = 'MAP_ID' AND R.respondent_ID = 'RESPONDENT_ID';" \
                .replace("MAP_ID", str(Map_id)).replace('RESPONDENT_ID', str(shape[7]))

            cursor.execute(sql)
            Questions = cursor.fetchall()

            for q in Questions:
                answer = q[1]
                if str(answer) == "":
                    answer = "None"
                line += answer+","

            file_content += line + "\n"

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return "1"

    except Exception as err:
        conn.close()
        print(err)
        return "0"

    return file_content


@app.route("/UpdateMapDetails", methods=['POST', 'GET'])
def update_map_details():
    username = session.get("Logged_in", None)

    authority = Classes.Authority(username)
    if authority.is_logged_in() is False:
        return render_template("error.html", Fail_Code=4)

    if request.method == "GET":
        Map_id = request.args.get("mapid")
    else:
        Map_id = request.form.get("Map_ID")

    try:
        conn = get_db()
        cursor = conn.cursor()

        sql = "SELECT map_id, map_creater, title, description, end_date, astext(Centroid(geo_boundery)), zoom " \
              "FROM Maps " \
              "WHERE map_creater = aes_encrypt('person','enckey') AND map_id = MAP_ID;".replace("person", username).replace("MAP_ID", Map_id)

        cursor.execute(sql)
        data = cursor.fetchone()
        if data is None:
            return render_template("error.html", Fail_Code=2)

        Map = {}
        Map["id"] = data[0]
        Map["creater"] = data[1]
        Map["title"] = data[2]
        Map["description"] = data[3]
        date = str(data[4])
        Map["end_date"] = date[5:7] + "/" + date[8:10] + "/" + date[:4]
        Map['center'] = (str(data[5]).strip("POINT(").strip(")")).replace(" ", ",")
        Map['zoom'] = str(data[6])

        # The GET method reads already registered info from map and send it as a response
        if request.method == 'GET':
            Map_id = request.args.get("mapid")

            # TODO: Reading registered Categories
            sql = "SELECT category_ID, category_name, category_type, category_image_or_color " \
                  "FROM Maps_Categories WHERE map_id = " + str(Map_id) + ";"
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

            # TODO: Reading registered Questions
            sql = "SELECT question_ID, question FROM Maps_Questions " \
                  "WHERE map_id = MAP_ID;".replace("MAP_ID", str(Map_id))
            cursor.execute(sql)
            data = cursor.fetchall()
            questions = []
            for entry in data:
                question = {
                    "ID": entry[0],
                    "question": entry[1]
                }
                questions.append(question)

            # TODO: Reading interviewers for this map
            sql = "SELECT username FROM Maps_Interviewers WHERE map_id = MAP_ID;".replace("MAP_ID", str(Map_id))
            cursor.execute(sql)
            data = cursor.fetchall()
            interviewers = []
            for entry in data:
                interviewers.append(entry[0])

            # TODO: Reading administrators for this map
            sql = "SELECT username FROM Maps_Administrators WHERE map_id = MAP_ID;".replace("MAP_ID", str(Map_id))
            cursor.execute(sql)
            data = cursor.fetchall()
            administrators = []
            for entry in data:
                administrators.append(entry[0])

            conn.close()
            return render_template("update_map_details.html", Map=Map, points=points_categories,
                                           roads=roads_categories, areas=areas_categories, questions=questions,
                                           interviewers=interviewers, administrators=administrators)

        # The POST method handels the changing on the map
        else:
            map_id = request.form.get("Map_ID")
            title = request.form.get("title")
            date = request.form.get('date')
            expiry_date = (date[6:] + "-" + date[0:2] + "-" + date[3:5])
            description = request.form.get("description")

            ## TODO: update map details
            sql = "UPDATE  Maps " \
                  "SET title = 'TITLE', description ='DESCRIPTION', end_date = 'END_DATE' " \
                  "WHERE map_id = MAP_ID;"
            sql = sql.replace("TITLE", title)
            sql = sql.replace("DESCRIPTION", description)
            sql = sql.replace("END_DATE", expiry_date)
            sql = sql.replace("MAP_ID", map_id)

            cursor.execute(sql)

            ## TODO: add new categories
            points_categories = request.form.getlist("point_categories")
            roads_categories = request.form.getlist("road_categories")
            areas_categories = request.form.getlist("area_categories")
            old_categories = request.form.getlist("old_categories")

            for category in list(points_categories + roads_categories + areas_categories):
                if category not in old_categories:
                    cat = category.split(',')
                    sql = "INSERT INTO Maps_Categories(category_name, category_type, category_image_or_color, map_id) " \
                          "VALUES(%s,%s,%s,%s);"
                    cursor.execute(sql, (cat[0], cat[1], cat[2], map_id))

            ## TODO: add new administrators and interviwers
            administrators = request.form.getlist("Administrators")
            interviewers = request.form.getlist("Interviewers")
            old_administrators = request.form.getlist("old_administrators")
            old_interviewers = request.form.getlist("old_interviewers")

            for interviewer in interviewers:
                if interviewer not in old_interviewers:
                    sql = "INSERT INTO Maps_Interviewers(username, map_id) VALUES(%s, %s);"
                    cursor.execute(sql, (interviewer, map_id))

                    for administrator in administrators:
                        if administrator not in old_administrators:
                            sql = "INSERT INTO Maps_Administrators(username, map_id) VALUES(%s, %s);"
                            cursor.execute(sql, (administrator, map_id))

            ## TODO: add new Questions, dont forget to add answers to allready registered respondents
            old_questions = request.form.getlist("old_questions")
            questions = request.form.getlist("questions")

            for question in questions:
                if question not in old_questions:
                    sql = "INSERT INTO Maps_Questions(question, map_id) VALUES(%s, %s);"
                    cursor.execute(sql, (question, map_id))
                    new_question_id = cursor.lastrowid
                    sql = "SELECT respondent_ID FROM Maps_Respondents WHERE map_id = MAP_ID;"\
                        .replace("MAP_ID", str(map_id))
                    cursor.execute(sql)
                    respondents_ids = cursor.fetchall()
                    for respondent_id in respondents_ids:
                        sql = "INSERT INTO Respondent_Answers(respondent_ID, question_ID, Answer) VALUES(%s, %s, '');"
                        cursor.execute(sql, (respondent_id[0], new_question_id))

            conn.commit()
            conn.close()
            return redirect("showmaps")

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return render_template("error.html", Fail_Code=1)

    except Exception as err:
        conn.close()
        print(err)
        return render_template("error.html", Fail_Code=0)


@app.route("/FeedbackArena", methods=['POST', 'GET'])
def feedbacks():
    username = session.get("Logged_in", None)
    authority = Classes.Authority(username)

    conn = get_db()
    cursor = conn.cursor()
    if request.method == "GET":
        try:
            if authority.is_logged_in() is False:
                return render_template("error.html", Fail_Code=4)

            mapid = request.args.get('mapid')
            all_users = authority.get_map_users(mapid)
            if type(all_users) == int:
                return render_template("error.html", Fail_Code=all_users)

            sql = "SELECT first_name, last_name, date, cmt FROM Feedbacks as F JOIN Persons as P On F.user = P.username WHERE F.map_id = MAP_ID;".replace("MAP_ID", str(mapid))
            cursor.execute(sql)
            data = cursor.fetchall()
            feedbacks = []
            for entry in data:
                feedback = {
                    "writer": entry[0]+" "+entry[1],
                    "date_and_time": entry[2],
                    "content": entry[3]
                }
                feedbacks.append(feedback)
            feedbacks = reversed(feedbacks)

            return render_template("feedback.html", feedbacks = feedbacks, Map_ID=mapid)
            conn.close()

        except mysql.connector.Error as err:
            conn.close()
            print(err.msg)
            return render_template("error.html", Fail_Code=1)
        except Exception as err:
            conn.close()
            print(err)
            return render_template("error.html", Fail_Code=0)

    elif request.method == "POST":
        try:
            if authority.is_logged_in() is False:
                return "4"
            map_id = request.form.get("Map_ID")
            all_users = authority.get_map_users(map_id)
            if type(all_users) == int:
                return str(all_users)

            username = session.get("Logged_in", None)
            content = request.form.get("Content");

            sql = "INSERT INTO Feedbacks(map_id, user, cmt) VALUES(%s,aes_encrypt(%s,'enckey'),%s);"
            cursor.execute(sql,(map_id, username, content))
            conn.commit()
            sql = "SELECT first_name, last_name FROM Persons WHERE username = aes_encrypt('Username','enckey')".replace("Username",username)
            cursor.execute(sql)
            data = cursor.fetchone()
            full_name = data[0]+" "+data[1]
            conn.close()
            return full_name

        except mysql.connector.Error as err:
            conn.close()
            print(err.msg)
            return "1"
        except Exception as err:
            conn.close()
            print(err)
            return "0"

    else:
        return "Unknown request"

    return render_template("feedback.html", maps=maps, feedo=feedo)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)