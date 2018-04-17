from flask import Flask, render_template, url_for, request, json, g, session, redirect
import mysql.connector
import datetime


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

class Authority:
    def __init__(self, username):
        self.username = username    # instance variable unique to each instance

    def get_all_map_users(self, map_id):
        conn = get_db()
        cursor = conn.cursor()

        try:
            Interviewers = []
            sql = "SELECT cast(aes_decrypt(M.username, 'enckey') AS CHAR(20)), e_post " \
                  "FROM Maps_Interviewers AS M JOIN Persons AS P " \
                  "ON M.username= P.username " \
                  "WHERE map_id = MAP_ID;".replace("MAP_ID", str(map_id))
            cursor.execute(sql)
            data = cursor.fetchall()
            for entry in data:
                interviewer = {"username": entry[0], "email": entry[1]}
                Interviewers.append(interviewer)

            Administrators = []
            sql = "SELECT cast(aes_decrypt(M.username, 'enckey') AS CHAR(20)), e_post " \
                  "FROM Maps_Administrators AS M JOIN Persons AS P " \
                  "ON M.username= P.username " \
                  "WHERE map_id = MAP_ID;".replace("MAP_ID", str(map_id))

            cursor.execute(sql)
            data = cursor.fetchall()
            for entry in data:
                Administrator = {"username": entry[0], "email": entry[1]}
                Administrators.append(Administrator)

            return (Interviewers, Administrators)

        except mysql.connector.Error as err:
            conn.close()
            print(err.msg)
            return (1, 1)

        except Exception as err:
            conn.close()
            print(err)
            return (0, 0)

    def is_logged_in(self):
        if self.username is not None:
            return True
        else:
            return False

    def get_map_users(self, map_id):
         try:
             conn = get_db()
             cursor = conn.cursor()
             sql = "SELECT cast(aes_decrypt(username, 'enckey') AS CHAR(20)) " \
                   "FROM Maps_Interviewers WHERE map_id = MAP_ID " \
                   "UNION " \
                   "SELECT cast(aes_decrypt(username, 'enckey') AS CHAR(20)) " \
                   "FROM Maps_Administrators WHERE map_id = MAP_ID;".replace("MAP_ID", map_id)
             cursor.execute(sql)
             data = cursor.fetchall()
             Users = []
             for entry in data:
                 Users.append(entry[0])

             if self.username not in Users:
                 return 2

             return Users

         except mysql.connector.Error as err:
             conn.close()
             print(err.msg)
             print("here class")
             return 1

         except Exception as err:
             conn.close()
             print(err)
             return 0

    def is_map_valid(self, map_id):

         conn = get_db()
         cursor = conn.cursor()
         sql = "SELECT end_date FROM Maps WHERE map_id = MAP_ID;".replace("MAP_ID", map_id)
         try:
             cursor.execute(sql)
             expiry_date = cursor.fetchall()[0][0]
             if expiry_date < datetime.date.today():
                 return 3

         except mysql.connector.Error as err:
             conn.close()
             print(err.msg)
             return 1

         except Exception as err:
             conn.close()
             print(err)
             return 0

