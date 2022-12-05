import storage_pb2
import storage_pb2_grpc
import grpc
import sys
from auth_client import AuthClient


class StorageClient:
    def __init__(self, auth_server, storage_server_id):
        self.auth = AuthClient(auth_server)

        self.host = storage_server_id.split(':')[0]
        self.port = storage_server_id.split(':')[1]
        channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        self.stub = storage_pb2_grpc.StorageStub(channel)
        print("Connected to StorageServer at {}:{}".format(self.host, self.port))

    def authenticate(self, identifier, password):
        # Authenticate with the auth server
        status = self.auth.Authenticate(identifier, password)
        return status

    def insert(self, key, value):
        # Check if the user is authenticated
        if self.auth.secret is None:
            return -9
        
        # Insert a key-value pair into the storage server
        result = self.stub.Insert(storage_pb2.InsertRequest(
            key=key, value=value, secret=self.auth.secret))
        return result.status

    def query(self, key):
        # Query the storage server for the value of a key
        result = self.stub.Get(storage_pb2.GetRequest(
            key=key, secret=self.auth.secret))
        return result.value

    def terminate(self):
        # Terminate the storage server
        return self.stub.Terminate(storage_pb2.TerminateRequest())

    def finish(self):
        # Finish the auth server
        return self.auth.Finish()

    def __str__(self) -> str:
        return f"StorageClient(storage_server={self.storage_server}, auth_server={self.auth_server}, secret={self.secret}, authenticated={self.authenticated})"

    def __repr__(self) -> str:
        return self.__str__()

    def run(self):
        while True:
            commands = input("Command: ")
            command = commands.split(" ")

            if command[0] == "A":
                print(self.authenticate(command[1], int(command[2])))
            elif command[0] == "I":
                print(self.insert(int(command[1]), " ".join(command[2:])))
            elif command[0] == "C":
                print(self.query(int(command[1])))
            elif command[0] == "T":
                self.terminate()
                break
            elif command[0] == "F":
                self.finish()
                break


if __name__ == "__main__":
    storage_client = StorageClient(sys.argv[1], sys.argv[2])
    storage_client.run()
