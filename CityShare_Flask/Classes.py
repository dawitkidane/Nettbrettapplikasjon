class Authority:
    def __init__(self, username):
        self.username = username    # instance variable unique to each instance

    def is_logged_in(self):
        if self.username is not None:
            return True
        else:
            return False

    def is_administrator(self, map_id):
        sql = "SELECT username FROM Maps_Administrators WHERE username = 'Mohammed' AND map_id = 1;"

        print("2"+self.username)
        return

    def is_intervjuer(self, map_id):
        sql = "SELECT username FROM Maps_Interviewers WHERE username = 'Dawit' AND map_id = 1;"
        print("3"+self.username)
        return

    def has_access_to_map(self, map_id):
        SQL = "SELECT username FROM Maps_Interviewers WHERE map_id = 1 " \
              "UNION" \
              "SELECT username FROM Maps_Administrators WHERE map_id = 1;"
        print("4"+self.username)
        return

    def get_map_intervjuers(self, map_id):
        sql = "SELECT username FROM Maps_Interviewers WHERE map_id = 1;"
        print("4"+self.username)
        return

    def get_map_administrators(self, map_id):
        sql = "SELECT username FROM Maps_Administrators WHERE map_id = 1;"
        print("4"+self.username)
        return
