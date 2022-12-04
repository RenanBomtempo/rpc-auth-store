import sys
import secrets

TOKEN_SIZE = 32


class User:
    def __init__(self, secret, password, permissions):
        self.secret = secret
        self.password = password
        self.permissions = permissions


class AuthServer:
    def __init__(self, port, admin_password):
        self.port = port
        self.initialize(admin_password)

    def initialize(self, admin_password):
        admin_secret = secrets.token_bytes(TOKEN_SIZE)
        self.users = {"super": User(admin_secret, admin_password, "SP")}
        self.authentications = {admin_secret: "SP"}

    def get_user_password(self, username):
        return self.users[username].password

    def get_user_permissions(self, username):
        return self.users[username].permissions

    def get_user_secret(self, username):
        if username not in self.users:
            return None
        return self.users[username].secret

    def set_user_secret(self, username, secret):
        if username not in self.users:
            print("ERROR: User does not exist")
            return -1

        old_secret = self.get_user_secret(username)
        if old_secret in self.authentications:
            permissions = self.authentications.pop(old_secret)
        else:
            permissions = self.get_user_permissions(username)

        self.authentications[secret] = permissions
        return 0

    def set_user_password(self, username, password):
        if username not in self.users:
            print("ERROR: User does not exist")
            return -1

        self.users[username].password = password
        return 0

    def set_user_permissions(self, username, permissions):
        if username not in self.users:
            print("ERROR: User does not exist")
            return -1

        self.users[username].permissions = permissions
        return 0


    def create_user(self, username, password, permissions, secret):
        if secret != self.users['super'].secret:
            print("ERROR: Only the admin can create users")
            return -1
        if username in self.users:
            print("ERROR: User already exists")
            return -2
        self.users[username] = User(secrets.token_bytes(
            TOKEN_SIZE), password, permissions)
        return 0
