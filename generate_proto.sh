#!/bin/bash

protoc --go_out=grpc-server/ --go-grpc_out=grpc-server/ scrape.proto
