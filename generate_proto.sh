#!/bin/bash

protoc --go_out=grpc-server/ --go-grpc_out=grpc-server/ --grpc-web_out=import_style=commonjs,mode=grpcweb:web-client/ scrape.proto
./web-client/node_modules/.bin/grpc_tools_node_protoc --js_out=import_style=commonjs,binary:web-client/ --grpc_out=grpc_js:web-client/ scrape.proto
