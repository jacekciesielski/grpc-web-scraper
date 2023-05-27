package main

import (
  "context"
  "flag"
  "fmt"
  "log"
  "math/rand"
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

var letters = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

func randSeq(n int) string {
    b := make([]rune, n)
    for i := range b {
        b[i] = letters[rand.Intn(len(letters))]
    }
    return string(b)
}

func makeInnerTypeMember(n int) []*pb.InnerType {
  ret := make([]*pb.InnerType, n)
  for i := range ret {
    ret[i] = new(pb.InnerType)
    ret[i].I = int32(i)
  }

  return ret
}

func (s *server) TryScraping(ctx context.Context, in *pb.ScrapeRequest) (*pb.ScrapeReply, error) {
  log.Printf("Received request string_lenght=%d inner_type_lenght=%d", in.GetStringLenght(), in.GetInnerTypeLenght())
  reply := pb.ScrapeReply{IntField: 100, StringField: randSeq(int(in.GetStringLenght()))}
  reply.InnerTypeFields = makeInnerTypeMember(int(in.GetInnerTypeLenght()))
  return &reply, nil
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
