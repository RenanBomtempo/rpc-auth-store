
import grpc
import auth_pb2_grpc
import auth_pb2
import sys
sys.path.append("..")


class AuthClient:
    def __init__(self, service_id: str):
        self.host = service_id.split(':')[0]
        self.port = service_id.split(':')[1]
        self.secret = None
        
        channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        self.stub = auth_pb2_grpc.AuthStub(channel)
        print("Connected to AuthServer at {}:{}".format(self.host, self.port))


    def Authenticate(self, identifier: str, password: int):
        result = self.stub.Authenticate(auth_pb2.AuthenticateRequest(
            identifier=identifier, password=password))
        if result.status == 0:
            self.secret = result.secret
        if result.status == -1:
            self.secret = None
        return result.status

    def CreateUser(self, identifier: str, password: int, permissions: str):
        result = self.stub.CreateUser(auth_pb2.CreateUserRequest(
            identifier=identifier, password=password, permissions=permissions, secret=self.secret))
        return result.status

    def VerifyAccess(self, secret):
        if secret is None:
            return -9
        else:
            result = self.stub.VerifyAccess(auth_pb2.VerifyAccessRequest(secret=secret))
            return result.permissions

    def Finish(self):
        return self.stub.FinishExecution(auth_pb2.FinishExecutionRequest())

    def run(self):
        while True:
            commands = input("Command: ")
            command = commands.split(" ")
            
            if command[0] == "A":
                print(self.Authenticate(command[1], int(command[2])))
            elif command[0] == "C":
                print(self.CreateUser(command[1], int(command[2]), command[3]))
            elif command[0] == "V":
                print(self.VerifyAccess(self.secret))
            elif command[0] == "F":
                self.Finish()
                break


if __name__ == "__main__":
    # Cria o cliente
    client = AuthClient(sys.argv[1])

    # Lê a entrada padrão
    client.run()
