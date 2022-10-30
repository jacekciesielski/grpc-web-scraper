const {ScrapeRequest} = require('./scrape_pb.js');
const {ScrapeClient} = require('./scrape_grpc_web_pb.js');

function main() {
  var client = new ScrapeClient('http://localhost:8080');
  var request = new ScrapeRequest();
  request.setStringLenght(1024);
  request.setInnerTypeLenght(10);

  client.tryScrapping(request, {}, function(err, response) {
    console.log('Response ', response.toObject());
  })
}

main();
