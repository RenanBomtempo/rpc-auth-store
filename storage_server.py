import storage_pb2
import storage_pb2_grpc
import grpc
import sys
import threading
from auth_client import AuthClient
from concurrent import futures


class StorageServer(storage_pb2_grpc.StorageServicer):
    def __init__(self, stop_event, port, auth_server_id: str):
        self.stop_event = stop_event
        self.port = port
        self.dict = {}
        self.auth = AuthClient(auth_server_id)
        print("StorageServer initialized")

    def Insert(self, request, context):
        secret = request.secret
        key = request.key
        value = request.value

        access = self.auth.VerifyAccess(secret)
        if access == "RW":
            self.dict[key] = value
            return storage_pb2.InsertReply(status=0)
        if access == "RO":
            return storage_pb2.InsertReply(status=-1)
        if access == "NE":
            return storage_pb2.InsertReply(status=-2)
        if access == "SP":
            return storage_pb2.InsertReply(status=-3)

    def Get(self, request, context):
        secret = request.secret
        key = request.key

        if self.auth.VerifyAccess(secret) in ["RO", "RW"]:
            val = self.dict.get(key, None)
        else:
            val = ""
        return storage_pb2.GetReply(value=val)

    def Terminate(self, request, context):
        self.stop_event.set()
        return storage_pb2.TerminateReply(status=0)
        


def serve():
    port = int(sys.argv[1])
    auth_server_id = sys.argv[2]

    stop_event = threading.Event()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    storage_pb2_grpc.add_StorageServicer_to_server(
        StorageServer(stop_event, port, auth_server_id), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"StorageServer started, listening on port {port}")
    stop_event.wait()
    server.stop()


if __name__ == "__main__":
    serve()
