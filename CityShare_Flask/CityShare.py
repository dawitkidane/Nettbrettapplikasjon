from flask import Flask, render_template, url_for, request, json, g, session, redirect
import mysql.connector

app = Flask(__name__)
app.secret_key = "any random string"


def get_db():
    if not hasattr(g, '_database'):
        g._database = mysql.connector.connect(host='sql2.freemysqlhosting.net',
                                              user='sql2217838',
                                              passwd='cR3!bC4!',
                                              db='sql2217838')
    return g._database


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
              "VALUES(%s,%s,%s,%s,%s,%s);"
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
            sql = "SELECT login_pass, first_name, last_name, e_post, telephone " \
                  "FROM Persons " \
                  "WHERE username = 'USERNAME'".replace('USERNAME', username)
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
                  "SET login_pass = 'PASS', first_name = 'FIRST_NAME', " \
                  "last_name = 'LAST_NAME', e_post = 'MAIL', telephone = 'TELE' " \
                  "WHERE username = 'USERNAME';".replace('USERNAME', username)
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
    session.pop('is_Admin', None)
    return render_template('home.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db()
    cursor = conn.cursor()
    sql = "SELECT COUNT(username) FROM Persons WHERE BINARY username = %s AND BINARY login_pass = %s LIMIT 0, 1;"
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
    sql = "SELECT username FROM Persons where username = 'search' or e_post = 'search';".replace('search', username)
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
    if map_creater is None:
        return render_template("error.html", msg="Du ma vaere innlogget for a kunne lage et kart !")

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
              "VALUES(%s,%s,%s,%s," + geo_boundery + ",%s);"
        try:
            cursor.execute(sql, (map_creater, title, description, enddate, geo_zoom))
            conn.commit()
            Map_id = cursor.lastrowid

            for user in Interviewers:
                sql = "INSERT INTO Maps_Interviewers(username, map_id) VALUES(%s,%s);"
                cursor.execute(sql, (user, Map_id))
                conn.commit()

            for user in Administrators:
                sql = "INSERT INTO Maps_Administrators(username, map_id) VALUES(%s,%s);"
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
            return render_template("new_map.html", Fail="En Feil har skjedd, prov igjen!")

        conn.close()
        return render_template("home.html")


@app.route("/showmaps", methods=['GET'])
def show_maps():
    username = session.get("Logged_in", None)
    if username is None:
        return render_template("error.html", msg="Du ma vaere innlogget for a se dine kart !")

    conn = get_db()
    cursor = conn.cursor()
    sql = "(SELECT map_id FROM Maps_Interviewers WHERE username = 'person')" \
          "UNION ALL" \
          "(SELECT map_id FROM Maps_Administrators WHERE username = 'person');".replace('person', str(username))
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        mapids = []
        for entry in set(data):
            mapids.append(entry[0])

        if mapids.__len__() == 0:
            return render_template("view_maps.html", maps={}, msg="Det er ingen registrerte kart pa deg!")

        maps = []
        for mapid in mapids:
            map = {
                "mapid": mapid,
            }
            conn = get_db()
            cursor = conn.cursor()

            sql = "SELECT map_creater, title, date(start_date), end_date, description, astext(Centroid(geo_boundery)), zoom FROM Maps WHERE map_id = " + str(
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
        return render_template("view_maps.html", maps={}, Fail="En feil har skjedd, prov igjen!")

    conn.close()
    return render_template("view_maps.html", maps=maps)


@app.route("/EditMap", methods=['GET'])
def edit_map():
    mapid = request.args.get('mapid')
    username = session.get("Logged_in", None)
    if username is None:
        return render_template("error.html", msg="Du ma vaere innlogget for a se ditt kart !")

    conn = get_db()
    cursor = conn.cursor()

    # TODO: Getting the usernames and email for the Interviwers and Administrators
    Interviewers = []
    Administrators = []
    sql = "SELECT M.username, e_post FROM Maps_Interviewers AS M JOIN Persons AS P ON M.username = P.username " \
          "WHERE map_id = 'MAP_ID';".replace("MAP_ID", str(mapid))
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        for entry in data:
            interviewer = {"username": entry[0], "email": entry[1]}
            Interviewers.append(interviewer)

        sql = "SELECT M.username, e_post FROM Maps_Administrators AS M JOIN Persons AS P ON M.username = P.username " \
              "WHERE map_id = 'MAP_ID';".replace("MAP_ID", str(mapid))

        cursor.execute(sql)
        data = cursor.fetchall()
        for entry in data:
            Administrator = {"username": entry[0], "email": entry[1]}
            Administrators.append(Administrator)

        # TODO: Check if the user logged in has right to access this map
        has_right = False
        all_users = Administrators + Interviewers
        for user in all_users:
            if user["username"] == username:
                has_right = True
                break
        if has_right == False:
            return render_template("view_maps.html", Fail="Du har ikke tilgang til dette kartet!")

        # TODO: Reading map details from database
        sql = "SELECT map_creater, title, description, start_date, end_date, astext(geo_boundery), zoom ,map_id " \
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

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return render_template("view_maps.html", Fail="En feil har skjedd, prov igjen!")

    conn.close()
    return render_template("edit_map.html", map=map, points_categories=points_categories,
                           roads_categories=roads_categories, questions=questions,
                           areas_categories=areas_categories)


@app.route("/RegisterRespondoent", methods=['POST'])
def RegisterRespondoent():
    Respondoent = json.loads(request.form.get('Respondoent'))
    Shapes = json.loads(request.form.get('Shapes'))
    Map_id = request.form.get('Map_id')
    logged_in_user = session.get("Logged_in", None)

    # TODO Insert/create new respondent
    conn = get_db()
    cursor = conn.cursor()
    sql = "INSERT INTO Maps_Respondents(map_id) VALUES(Map_id);".replace("Map_id", str(Map_id))
    try:
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
                  "VALUES(%s, %s, " + center + ", " + area_or_path + ", %s, %s, %s, %s);"

            cursor.execute(sql, (str(shape['category_ID']), str(logged_in_user), shape['title'],
                                 shape['description'], shape['rating'], str(Respondoent_id)))

            conn.commit()

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return "Fail"

    conn.close()
    return "Success"


@app.route("/ViewMapResult", methods=['GET'])
def view_map_result():
    mapid = request.args.get('mapid')
    username = session.get("Logged_in", None)
    if username is None:
        return render_template("error.html", msg="Du ma vaere innlogget for a se ditt kart !")

    conn = get_db()
    cursor = conn.cursor()

    # TODO: Check if a user is logged in
    if username is None:
        return render_template("error.html")

    # TODO: Determine if the logged_in_user who is requesing the map is an administrator or just an interviewer
    Interviewers = []
    Administrators = []
    sql = "SELECT M.username, e_post FROM Maps_Interviewers AS M JOIN Persons AS P ON M.username = P.username " \
          "WHERE map_id = 'MAP_ID';".replace("MAP_ID", str(mapid))
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        for entry in data:
            interviewer = {"username": entry[0], "email": entry[1]}
            Interviewers.append(interviewer)

        sql = "SELECT M.username, e_post FROM Maps_Administrators AS M JOIN Persons AS P ON M.username = P.username " \
              "WHERE map_id = 'MAP_ID';".replace("MAP_ID", str(mapid))
        cursor.execute(sql)
        data = cursor.fetchall()
        for entry in data:
            Administrator = {"username": entry[0], "email": entry[1]}
            Administrators.append(Administrator)

        Administrators_names = []
        for user in Administrators:
            Administrators_names.append(user["username"])

        # TODO: Reading the map_details
        sql = "SELECT map_creater, title, description, start_date, end_date, astext(geo_boundery), zoom ,map_id " \
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
        sql = "SELECT S.shape_id, S.shape_creater, astext(S.center), astext(S.area_or_path), S.title, S.description, " \
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


    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return render_template("error.html", Fail="En feil har skjedd, prov igjen!")

    conn.close()

    all_users = []
    if username in Administrators_names:
        for user in (Administrators + Interviewers):
            if user not in all_users:
                all_users.append(user)

    return render_template("view_map_result.html", Users=all_users, Map=map,
                           Questions=questions, Questions_response=questions_response,
                           Points=points, Areas=areas, Roads=roads)


@app.route("/Edit_Shape", methods=['POST'])
def edit_shape():
    map_id = request.form.get("map_id")
    username = session.get("Logged_in")
    Shape_id = request.form.get("shape_id")
    Task = request.form.get("task")

    conn = get_db()
    cursor = conn.cursor()

    try:
        ## TODO: Check to see if the logged_in user is an adminstrator of this map or her/she is creater of this shape
        sql = "SELECT shape_creater FROM Shapes WHERE shape_creater = 'USERNAME' AND shape_id = SHAPE_ID " \
              "UNION ALL " \
              "SELECT username FROM Maps_Administrators WHERE username = 'USERNAME' AND MAP_ID = 1;"
        sql = sql.replace("USERNAME", username)
        sql = sql.replace("MAP_ID", map_id)
        sql = sql.replace("SHAPE_ID", Shape_id)
        cursor.execute(sql)
        data = cursor.fetchall()
        names = []
        for name in data:
            names.append(name[0])
        if username not in names:
            return "Du har ikke rettighet til a gjore dette!"

        ## TODO: Do the requested task to update
        if Task == "Update":
            Title = request.form.get("title")
            Description = request.form.get("description")
            Rating = request.form.get("rating")
            sql = "UPDATE Shapes " \
                  "SET title = 'TITLE', description = 'DESCRIPTION', rate = RATING " \
                  "WHERE shape_id = SHAPE_ID;".replace("SHAPE_ID", Shape_id)
            sql = sql.replace('TITLE', Title)
            sql = sql.replace('DESCRIPTION', Description)
            sql = sql.replace('RATING', Rating)
            cursor.execute(sql)
            conn.commit();

        ## TODO: Do the requested task to delete
        elif Task == "Delete":
            sql = "DELETE FROM Shapes WHERE shape_id = SHAPE_ID;".replace("SHAPE_ID", Shape_id)
            cursor.execute(sql)
            conn.commit()

        ## TODO: in case the task is not spesified
        else:
            conn.close()
            return "Unsupported Task"

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return "Error"

    return "Success"


@app.route("/DownloadMapAsCSVFile", methods=['POST'])
def Download_Map_As_CSV_File():
    username = session.get("Logged_in")
    Map_id = json.loads(request.form.get('Map_id'))
    Shapes_data = json.loads(request.form.get('Data'))
    Respondents = json.loads(request.form.get("Respondoents"))

    conn = get_db()
    cursor = conn.cursor()

    # TODO: Check if a user is logged in
    if username is None:
        return render_template("error.html",
                               Fail="Du ma vaere logget inn for a kunne laste ned ditt kart som en .csv fil!")

    # TODO: Determine if the logged_in_user who is requesing the map is an administrator or an interviewer
    All_Users = []
    sql = "(SELECT M.username FROM Maps_Administrators AS M JOIN Persons AS P ON M.username = P.username WHERE map_id = MAP_ID)" \
          "UNION" \
          "(SELECT M.username FROM Maps_Interviewers AS M JOIN Persons AS P ON M.username = P.username WHERE map_id = MAP_ID);".replace(
        "MAP_ID", str(Map_id))
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        for entry in data:
            User = entry[0]
            All_Users.append(User)

        # TODO: checking if the current user name has right to this map
        if username not in All_Users:
            conn.close()
            return render_template("error.html", Fail="Du har ingen rettighet til dette kartet !")

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
            line = file_header
            line = line.replace("Map_ID", str(Map_id))
            line = line.replace("Map_bounds", str(map_bounds))

            # TODO: Read relevant shape's data from database
            sql = "SELECT astext(S.area_or_path), astext(S.center), S.shape_creater, S.title, S.description, " \
                  "S.rate, M.category_type, S.respondent_ID " \
                  "FROM Shapes S JOIN Maps_Categories M ON S.category_ID = M.category_ID " \
                  "WHERE map_id = 'MAP_ID' AND shape_id = 'SHAPE_ID';" \
                .replace("MAP_ID", str(Map_id)).replace("SHAPE_ID", str(shape_id))

            cursor.execute(sql)
            shape = cursor.fetchone()

            ## Map_ID,Map_bounds,Area_or_path_Coordinates,Center,Interviewer,Title,Description,Rating,Category_type,Respondent_ID
            line = line.replace("Map_ID", str(Map_id))
            line = line.replace("Map_bounds", str(map_bounds))
            line = line.replace("Area_or_path_Coordinates", str(shape[0]))
            line = line.replace("Center", str(shape[1]))
            line = line.replace("Interviewer", str(shape[2]))
            line = line.replace("Title", str(shape[3]))
            line = line.replace("Description", str(shape[4]))
            line = line.replace("Rating", str(shape[5]))
            line = line.replace("Category_type", str(shape[6]))
            line = line.replace("Respondent_ID", str(shape[7]))

            sql = "SELECT Q.question, R.Answer " \
                  "FROM Respondent_Answers AS R JOIN Maps_Questions AS Q ON R.question_ID = Q.question_ID " \
                  "WHERE map_id = 'MAP_ID' AND R.respondent_ID = 'RESPONDENT_ID';" \
                .replace("MAP_ID", str(Map_id)).replace('RESPONDENT_ID', str(shape[7]))

            cursor.execute(sql)
            Questions = cursor.fetchall()

            for q in Questions:
                line = line.replace(str(q[0]), str(q[1]))

            file_content += line + "\n"

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return "Fail"

    return file_content


@app.route("/UpdateMapDetails", methods=['POST', 'GET'])
def Update_Map_Details():
    username = session.get("Logged_in", None)
    if username is None:
        return render_template("error.html", msg="Du ma vaere innlogget for a se a kunne redigere ditt kart !")

    if request.method == "GET":
        Map_id = request.args.get("mapid")
    else:
        Map_id = request.form.get("Map_ID")

    try:
        conn = get_db()
        cursor = conn.cursor()

        sql = "SELECT map_id, map_creater, title, description, end_date, astext(Centroid(geo_boundery)), zoom " \
              "FROM Maps " \
              "WHERE map_creater = 'person' AND map_id = MAP_ID;".replace("person", username).replace("MAP_ID", Map_id)

        cursor.execute(sql)
        data = cursor.fetchone()
        if data is None:
            return render_template("error.html", msg="Du har ikke rettighet til a oppdatere dette kartet")

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
        return render_template("error.html", Fail="Noe Feil har skjedd, prov igjen")


def feedbacks(mapid):

    conn = get_db()
    cursor = conn.cursor()

    sql = "SELECT feedback_id FROM Feedbacks WHERE map_id = " + str(mapid) + ";"
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        feedids = []
        for entry in data:
            feedids.append(entry[0])

        feedo = []
        for feed in reversed(feedids):
            fee = {
                "feedid": feed,
            }
            conn = get_db()
            cursor = conn.cursor()

            sql = "SELECT P.first_name, P.last_name, date, cmt FROM Feedbacks AS F JOIN Persons AS P ON P.username = F.user " \
                  "WHERE feedback_id = 'MAP_ID';".replace("MAP_ID", str(feed))

            try:
                cursor.execute(sql)
                data = cursor.fetchone()
                fee['firstname'] = data[0]
                fee['lastname'] = data[1]
                fee['date'] = data[2]
                fee['cmt'] = data[3]
                fee['mapid'] = mapid
                feedo.append(fee)

            except mysql.connector.Error as err:
                conn.close()
                print(err.msg)

        map = {
            "mapid": mapid,
        }
        maps= []
        sql = "SELECT map_creater, title, date(start_date), end_date, description, astext(Centroid(geo_boundery)), zoom FROM Maps WHERE map_id = " + str(
            mapid) + ";"

        cursor.execute(sql)
        test = cursor.fetchone()
        map['creater'] = test[0]
        map['title'] = test[1]
        map['issuedate'] = str(test[2])
        map['expirydate'] = str(test[3])
        map['description'] = str(test[4])
        map['center'] = (str(test[5]).strip("POINT(").strip(")")).replace(" ", ",")
        map['zoom'] = str(test[6])
        map['mapid'] = str(mapid)

        maps.append(map)

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return "Failed"
    finally:
        conn.close()

    return render_template("feedback.html", maps=maps, feedo=feedo)

@app.route("/feedso/<int:mapid>")
def feedback(mapid):
    return feedbacks(mapid)


@app.route("/addfeedback/<int:mapid>", methods=['POST', 'GET'])
def addfeedback(mapid):
    mapid = mapid
    user = session.get("Logged_in")
    comment = request.form.get('cmt')

    conn = get_db()
    data = conn.cursor()
    sql = "INSERT INTO Feedbacks(map_id, user, cmt)" \
        "VALUES(%s,%s, %s);"

    try:
        data.execute(sql, (mapid, user, comment))
        conn.commit()

        return feedbacks(mapid)
    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)

    finally:
        conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0',port="5000")