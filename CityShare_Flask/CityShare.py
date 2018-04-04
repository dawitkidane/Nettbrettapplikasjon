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
        is_admin = row[1]

        Error = None

        if does_exist == 1:
            session["Logged_in"] = username

            if is_admin == 1:
                session["is_Admin"] = is_admin

            return render_template("home.html", Error=Error)


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
              "VALUES(%s,%s,%s,%s,"+geo_boundery+",%s);"
        try:
            cursor.execute(sql, (map_creater,title,description,enddate,geo_zoom))
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
            return render_template("new_map.html", Fail="En Feil har skjedd, prøv igjen!")

        conn.close()
        return render_template("home.html")

@app.route("/showmaps", methods=['GET'])
def show_maps():
    username = session.get("Logged_in")

    conn = get_db()
    cursor = conn.cursor()
    sql = "(SELECT map_id FROM Maps_Interviewers WHERE username = 'person')" \
          "UNION ALL" \
          "(SELECT map_id FROM Maps_Administrators WHERE username = 'person');".replace('person',str(username))
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        mapids = []
        for entry in data:
            mapids.append(entry[0])

        if mapids.__len__() == 0:
            return render_template("view_maps.html", maps={}, msg="Det er ingen registrerte kart på deg!")

        maps = []
        for mapid in mapids:
            map = {
                "mapid": mapid,
            }
            conn = get_db()
            cursor = conn.cursor()

            sql = "SELECT map_creater, title, date(start_date), end_date, description, astext(Centroid(geo_boundery)), zoom FROM Maps WHERE map_id = "+str(mapid)+";"

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
        return render_template("view_maps.html", maps={}, Fail="En feil har skjedd, prøv igjen!")

    conn.close()
    return render_template("view_maps.html", maps=maps)

@app.route("/EditMap", methods=['GET'])
def edit_map():
    mapid = request.args.get('mapid')
    username = session.get("Logged_in")

    conn = get_db()
    cursor = conn.cursor()

    # TODO: Getting the usernames and email for the Interviwers and Administrators
    Interviewers = []
    Administrators = []
    sql = "SELECT M.username, e_post FROM Maps_Interviewers AS M JOIN Persons AS P ON M.username = P.username " \
          "WHERE map_id = 'MAP_ID';".replace("MAP_ID",str(mapid))
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
        all_users = Administrators+Interviewers
        for user in all_users:
            if user["username"] == username:
                has_right = True
                break
        if has_right == False:
            return render_template("view_maps.html", Fail="Du har ikke tilgang til dette kartet!")


        # TODO: Reading map details from database
        sql = "SELECT map_creater, title, description, start_date, end_date, astext(geo_boundery), zoom ,map_id " \
              "FROM Maps " \
              "WHERE map_id = MAP_ID;".replace("MAP_ID",str(mapid))
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
        return render_template("view_maps.html", Fail="En feil har skjedd, prøv igjen!")

    conn.close()
    return render_template("edit_map.html", map=map, points_categories=points_categories,
                           roads_categories=roads_categories, questions=questions,
                           areas_categories=areas_categories)

@app.route("/ViewMapResult", methods=['GET'])
def view_map_result():
    mapid = request.args.get('mapid')
    username = session.get("Logged_in")

    conn = get_db()
    cursor = conn.cursor()

    # TODO: Check if a user is logged in
    if username is None:
        return render_template("error.html")

    # TODO: Determine if the logged_in_user who is requesing the map is an administrator or just an interviewer
    Interviewers = []
    Administrators = []
    sql = "SELECT M.username, e_post FROM Maps_Interviewers AS M JOIN Persons AS P ON M.username = P.username " \
          "WHERE map_id = 'MAP_ID';".replace("MAP_ID",str(mapid))
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
        return render_template("error.html", Fail="En feil har skjedd, prøv igjen!")

    conn.close()

    all_users = []
    if username in Administrators_names:
        for user in (Administrators + Interviewers):
            if user not in all_users:
                all_users.append(user)

    return render_template("view_map_result.html", Users=all_users, Map=map,
                           Questions=questions, Questions_response=questions_response,
                           Points=points, Areas=areas, Roads=roads)

@app.route("/ChangeMap", methods=['POST','GET'])
def ChangeMap():
    mapid = request.args.get('mapid')
    username = session.get("Logged_in")

    conn = get_db()
    cursor = conn.cursor()

    # TODO: Check if a user is logged in
    if username is None:
        return render_template("error.html")

    # TODO: Determine if the logged_in_user who is requesing the map is an administrator or just an interviewer
    Interviewers = []
    Administrators = []
    sql = "SELECT M.username, e_post FROM Maps_Interviewers AS M JOIN Persons AS P ON M.username = P.username " \
          "WHERE map_id = 'MAP_ID';".replace("MAP_ID",str(mapid))
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
        return render_template("error.html", Fail="En feil har skjedd, prøv igjen!")

    conn.close()

    all_users = []
    if username in Administrators_names:
        for user in (Administrators + Interviewers):
            if user not in all_users:
                all_users.append(user)

    return render_template("change_map.html", Users=all_users, Map=map,
                           Questions=questions, Questions_response=questions_response,
                           Points=points, Areas=areas, Roads=roads)

@app.route("/ChangeIt", methods=['POST','GET'])
def ChangeIt():

    if request.method == 'GET':
        print("here")
        return render_template("change_map.html")

    else:
        print("its happening")
        map_creater = session.get("Logged_in")
        title = request.form.get('title')
        description = request.form.get('description')
        mapid = request.args.get('mapid')
        print(mapid)

        date = request.form.get('date')
        enddate = date[6:] + "-" + date[0:2] + "-" + date[3:5]

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
        # sql = "UPDATE Shapes " \
        #       "SET title = '" + title + "', description = '" + description + "', rate = " + str(rating) + " " \
        #                                                                                                   "WHERE shape_id = " + str(
        #     shape_id) + ";"
        # try:
        #     cursor.execute(sql)
        #     conn.commit()
        ## TODO: ADD MAP TO DATABASE, 2 TABLES USERS AND MAPS
        conn = get_db()
        cursor = conn.cursor()
        sql = "UPDATE Maps " \
              "SET title = '" + title + "',description = '" + description + "',end_date = '" + enddate + "' " \
            "WHERE map_id = "+str(mapid)+";"
        try:
            cursor.execute(sql)
            conn.commit()


            for user in Interviewers:
                #sql = "INSERT INTO Maps_Interviewers(username, map_id) VALUES(%s,%s);"
                sql = "UPDATE Maps_Interviewers SET username = '" + user + "',map_id = '" + mapid + "';"

                cursor.execute(sql)
                conn.commit()

            for user in Administrators:
                #sql = "INSERT INTO Maps_Administrators(username, map_id) VALUES(%s,%s);"
                sql = "UPDATE Maps_Administrators SET username = '" + user + "',map_id = '" + mapid + "';"
                cursor.execute(sql)
                conn.commit()

            categories = points_categories + roads_categories + areas_categories
            for category in categories:
                cat = category.split(',')
                #sql = "INSERT INTO Maps_Categories(category_name, category_type, category_image_or_color, map_id) " \
                      #"VALUES(%s,%s,%s,%s);"

                sql = "UPDATE Maps_Categories SET category_name = '" + cat[0] + "',category_type = '" + cat[1] + "\
                      ""',category_image_or_color = '" + cat[2] + "',map_id = '" + mapid + "';"

                cursor.execute(sql)
                conn.commit()

            for question in questions:
                #sql = "INSERT INTO Maps_Questions(question, map_id) values(%s,%s);"
                sql = "UPDATE Maps_Questions SET question = '" + question + "',map_id = '" + mapid + "';"
                cursor.execute(sql)
                conn.commit()

        except mysql.connector.Error as err:
            conn.close()
            print(err.msg)
            return render_template("change_map.html", Fail="En Feil har skjedd, prøv igjen!")

        conn.close()
        return render_template("home.html")

@app.route("/RegisterRespondoent", methods=['POST'])
def RegisterRespondoent():
    Respondoent = json.loads(request.form.get('Respondoent'))
    Shapes = json.loads(request.form.get('Shapes'))
    Map_id = request.form.get('Map_id')
    logged_in_user = session.get("Logged_in")

    """
    for key in Respondoent:
        print(key+": "+str(Respondoent[key]))
    Where do you live ?: {'answer': 'Bergen', 'ID': 1}
    how old are you ?: {'answer': '18', 'ID': 3}
    what do you like to eat ?: {'answer': 'chicken', 'ID': 2}
    
    for key in Shapes:
        print(key+": "+str(Shapes[key]))
    1: {'title': 'point 2', 'type': 'POINT', 'category_ID': '1', 'creater': 'Mohammed', 'description': 'nr. 2', 'area_or_path': '', 'rating': '5', 'center': '(58.93767829819591, 5.803488164550799)'}
    0: {'title': 'POINT 1', 'type': 'POINT', 'category_ID': '2', 'creater': 'Mohammed', 'description': 'nr 1', 'area_or_path': '', 'rating': '2', 'center': '(58.935198189097356, 5.694998174316424)'}
    """

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
                  "VALUES(%s, %s, "+center+", "+area_or_path+", %s, %s, %s, %s);"

            cursor.execute(sql, (str(shape['category_ID']), str(logged_in_user), shape['title'],
                                 shape['description'], shape['rating'], str(Respondoent_id)))

            conn.commit()

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return "Fail"

    conn.close()
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
                               Fail="Du må være logget inn for å kunne laste ned ditt kart som en .csv fil!")

    # TODO: Determine if the logged_in_user who is requesing the map is an administrator or an interviewer
    All_Users = []
    sql = "(SELECT M.username FROM Maps_Administrators AS M JOIN Persons AS P ON M.username = P.username WHERE map_id = MAP_ID)" \
          "UNION" \
          "(SELECT M.username FROM Maps_Interviewers AS M JOIN Persons AS P ON M.username = P.username WHERE map_id = MAP_ID);".replace("MAP_ID", str(Map_id))
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
            file_header += ","+str(question[0])

        file_content = file_header+"\n"

        # TODO: Read map bounds
        sql = "SELECT astext(geo_boundery) FROM Maps WHERE map_id = 'MAP_ID';".replace("MAP_ID", str(Map_id))
        cursor.execute(sql)
        map_bounds = cursor.fetchone()[0]

        for shape_id in Shapes_data:
            line = file_header
            line = line.replace("Map_ID",str(Map_id))
            line = line.replace("Map_bounds",str(map_bounds))

            # TODO: Read relevant shape's data from database
            sql = "SELECT astext(S.area_or_path), astext(S.center), S.shape_creater, S.title, S.description, " \
                  "S.rate, M.category_type, S.respondent_ID " \
                  "FROM Shapes S JOIN Maps_Categories M ON S.category_ID = M.category_ID " \
                  "WHERE map_id = 'MAP_ID' AND shape_id = 'SHAPE_ID';"\
                .replace("MAP_ID", str(Map_id)).replace("SHAPE_ID", str(shape_id))

            cursor.execute(sql)
            shape = cursor.fetchone()

            ## Map_ID,Map_bounds,Area_or_path_Coordinates,Center,Interviewer,Title,Description,Rating,Category_type,Respondent_ID
            line = line.replace("Map_ID", str(Map_id))
            line = line.replace("Map_bounds", str(map_bounds))
            line = line.replace("Area_or_path_Coordinates",str(shape[0]))
            line = line.replace("Center",str(shape[1]))
            line = line.replace("Interviewer",str(shape[2]))
            line = line.replace("Title",str(shape[3]))
            line = line.replace("Description",str(shape[4]))
            line = line.replace("Rating",str(shape[5]))
            line = line.replace("Category_type",str(shape[6]))
            line = line.replace("Respondent_ID",str(shape[7]))

            sql = "SELECT Q.question, R.Answer " \
                  "FROM Respondent_Answers AS R JOIN Maps_Questions AS Q ON R.question_ID = Q.question_ID " \
                  "WHERE map_id = 'MAP_ID' AND R.respondent_ID = 'RESPONDENT_ID';"\
                    .replace("MAP_ID", str(Map_id)).replace('RESPONDENT_ID',str(shape[7]))

            cursor.execute(sql)
            Questions = cursor.fetchall()

            for q in Questions:
                line = line.replace(str(q[0]),str(q[1]))

            file_content += line+"\n"

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return "Fail"

    return file_content

@app.route("/feedback", methods=['GET'])
def feedback():

    conn = get_db()
    cursor = conn.cursor()
    sql = "SELECT feedback_id FROM Feedbacks;"
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

            sql = "SELECT name, cmt, date FROM Feedbacks WHERE feedback_id = " + str(
                feed) + ";"
            try:
                cursor.execute(sql)
                data = cursor.fetchone()
                fee['name'] = data[0]
                fee['cmt'] = data[1]
                fee['date'] = data[2]
                feedo.append(fee)

            except mysql.connector.Error as err:
                conn.close()
                print(err.msg)

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)
        return "Failed"
    finally:
        conn.close()

    return render_template("feedback.html", feedo=feedo)

@app.route("/addfeedback", methods=['POST'])
def addfeedback():
    name = request.form.get('name')
    comment = request.form.get('cmt')

    conn = get_db()
    cursor = conn.cursor()
    sql = "INSERT INTO Feedbacks(name, cmt)" \
        "VALUES(%s,%s);"

    try:
        cursor.execute(sql, (name, comment))
        conn.commit()

    except mysql.connector.Error as err:
        conn.close()
        print(err.msg)

    finally:
        conn.close()

    return render_template("home.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0')
