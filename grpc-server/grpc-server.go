package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"

	"google.golang.org/grpc"
  pb "grpc-web-scraper/grpc-server/grpc-web-scraper"
)

var (
	port = flag.Int("port", 9026, "The server port")
)

// server is used to implement helloworld.GreeterServer.
type server struct {
	pb.UnimplementedScrapeServer
}

func (s *server) TryScrapping(ctx context.Context, in *pb.ScrapeRequest) (*pb.ScrapeReply, error) {
	log.Printf("Received request")
  return &pb.ScrapeReply{IntField: 1, StringField: "ddd"}, nil
}

func main() {
	flag.Parse()
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	pb.RegisterScrapeServer(s, &server{})
	log.Printf("server listening at %v", lis.Addr())
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
