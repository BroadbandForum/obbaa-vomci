python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. tr451_vomci_sbi_message.proto
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. tr451_vomci_sbi_service.proto