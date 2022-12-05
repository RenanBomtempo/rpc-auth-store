# Makefile to run the Authenticator Server and the Client
arg1 = $(word 2, $(MAKECMDGOALS))
arg2 = $(word 3, $(MAKECMDGOALS))
STUBS = storage_pb2.py storage_pb2_grpc.py auth_pb2.py auth_pb2_grpc.python

clean:
	rm -f $(STUBS)

stubs:
	@echo	"Generating stubs..."
	@python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. auth.proto
	@python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. storage.proto


run_cli_ident:
	@echo "Running the Authentication Client"
	@python3 auth_client.py $(arg1) $(arg2)

run_serv_ident: 
	@echo "Running the Authentication Server"
	@python3 auth_server.py $(arg1) $(arg2)

run_serv_pares: 
	@echo "Running the Storage Server"
	@python3 storage_server.py $(arg1) $(arg2)

run_cli_pares: 
	@echo "Running the Storage Client"
	@python3 storage_client.py $(arg1) $(arg2)

