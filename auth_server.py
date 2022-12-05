import sys
from concurrent import futures
import secrets
import grpc
import auth_pb2
import auth_pb2_grpc
import threading

TOKEN_SIZE = 32

class User:
    def __init__(self, secret, password, permissions):
        self.secret = secret
        self.password = password
        self.permissions = permissions

    def __str__(self) -> str:
        return f"User(password={self.password}, permissions={self.permissions}, secret={int.from_bytes(self.secret, byteorder='big')})"

    def __repr__(self) -> str:
        return self.__str__()


class AuthServer(auth_pb2_grpc.AuthServicer):
    def __init__(self, stop_event, port, admin_password):
        self.stop_event = stop_event # Event to stop the thread
        self.port = port
        self.initialize(admin_password)
        print("AuthServer initialized")

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
            return -1

        self.users[username].secret = secret
        return 0

    def set_user_password(self, username, password):
        if username not in self.users:
            return -1

        self.users[username].password = password
        return 0

    def set_user_permissions(self, username, permissions):
        if username not in self.users:
            return -1

        self.users[username].permissions = permissions
        return 0

    def Authenticate(self, request, context):

        username = request.identifier
        password = request.password

        # Check if user exists and password is correct
        if username not in self.users:
            return auth_pb2.AuthenticateReply(status=-1, secret=b"\0" * TOKEN_SIZE)
        if self.get_user_password(username) != password:
            return auth_pb2.AuthenticateReply(status=-1, secret=b"\0" * TOKEN_SIZE)

        # Generate new secret and update user's previous secret
        new_secret = secrets.token_bytes(TOKEN_SIZE)

        # Update authentications
        old_secret = self.get_user_secret(username)
        if old_secret in self.authentications:
            permissions = self.authentications.pop(old_secret)
        else:
            permissions = self.get_user_permissions(username)

        self.authentications[new_secret] = permissions
        self.set_user_secret(username, new_secret)
        return auth_pb2.AuthenticateReply(status=0, secret=new_secret)

    def CreateUser(self, request, context):
        username = request.identifier
        password = request.password
        permissions = request.permissions
        secret = request.secret

        if secret != self.users['super'].secret:
            return auth_pb2.CreateUserReply(status=-1)
        if username in self.users:
            return auth_pb2.CreateUserReply(status=-2)
        self.users[username] = User(secrets.token_bytes(
            TOKEN_SIZE), password, permissions)
        print(self.users)
        return auth_pb2.CreateUserReply(status=0)


    def VerifyAccess(self, request, context):
        secret = request.secret
        if secret not in self.authentications:
            return auth_pb2.VerifyAccessReply(permissions="NE")
        return auth_pb2.VerifyAccessReply(permissions=self.authentications.get(secret))

    def FinishExecution(self, request, context):
        self.stop_event.set()
        return auth_pb2.FinishExecutionReply(users=len(self.users))


def serve():
    port = int(sys.argv[1])
    admin_password = int(sys.argv[2])

    stop_event = threading.Event()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    auth_pb2_grpc.add_AuthServicer_to_server(
        AuthServer(stop_event, port, admin_password), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"AuthServer started, listening on port {port}")
    stop_event.wait()
    server.stop()


if __name__ == "__main__":
    serve()
