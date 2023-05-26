# grpc-web-scraper

## Intro

The purpose of this project is to allow programmatic access to gRPC method calls aka _gRPC Web Scraping_. With its help you can take advantage of exposed gRPC web API to not only get the binary data it's serving, but also recover original Protocol Buffers payload data types via javascript API client code uses for decoding Protobuf messages.

### Prequisites - when can I use this project

The most common scenario is:

- You have found a website using gRPC web server
- with Protobuf serialized payload under the hood

Naturally, browser is not the most convenient way of accessing WWW data. You want a CLI tool, like True Hackers™ do. Or you just have a shady usecase in mind for the precious data that someone is not providing a sane API for accessing. Hey, I am not judging here.

## HOWTO

Below you can find description how to scrape a website with step by step examples made with a sample server attached in playground/ directory. Feel free to check it out and modify the server according to you needs.

### 1. Locate a method you want to scrape

Go to developer tools of your browser. In the screenshots I am using Firefox. I bet Chrome can do exactly the same.

![developer_tools](https://github.com/jacekciesielski/grpc-web-scraper/assets/111685433/ee872f91-d660-4716-8d0d-026829a0fffd)

Here I am going to use `Scrape.TryScraping` method of the playground server. playground/scrape.proto file contains the service definitions. Check it out as part of the exercise. It's a luxury we usually don't have in real life scenarios.

Open Network tab. Headers contain full URI. Copy it. It contains server name, namespace, service and method names.

E.g `http://localhost:8080/grpc_web_scraper.Scrape/TryScraping`

![uri](https://github.com/jacekciesielski/grpc-web-scraper/assets/111685433/720ef3c8-8fa5-4da8-ae3a-83e8f43c89c1)

### 2. Choose payload you're going to use for scraping.

Usually a server requires input data to give you any output. To start with something, try copying the payload used by the website. You can modify it later. There are [awesome protobuf binary encoding docs](https://protobuf.dev/programming-guides/encoding/). It will tell you how to modify payload.

Here I am going to copy the payload using Firefox's developer tools. I bet you can do the same at least with Chrome.

See request payload. Usually it's just a bunch of unicode characters.

![request_payload](https://github.com/jacekciesielski/grpc-web-scraper/assets/111685433/2cae64ec-a468-4a9a-9974-0e5ec47a92ec)

You need to save it somehow. I found _the hard way_ that just copying and pasting as well as [saving .har file doesn't work too well](https://indigo.re/posts/2020-10-09-har-is-clumsy.html). I mean many times it works like charm, but some characters are lost for whatever reason. The way I do it is rough and probably a bit stupid, but, hey, it works.

Open stack trace.

![stack_trace](https://github.com/jacekciesielski/grpc-web-scraper/assets/111685433/bfeb61f6-e119-45b4-8c4d-bc87bce38042)

Set breakpoint on a frame just before sending the data. The js source was transformed by `browserify`. Don't get too attached to function names and position in stack trace, because that varies from one bundling tool to another, but it's easy to figure out just walking through a few stack trace frames up. The data you look for is stored in one of variables. Here it is called `b`. Copy the int array.

![debugger_array](https://github.com/jacekciesielski/grpc-web-scraper/assets/111685433/4e6f23fe-2ae2-48d6-829f-99c2b31525ac)

E.g `0, 0, 0, 0, 5, 8, 128, 8, 16, 10`

### 3. Lookup response class name

This is the last bit you need. The response class holds deserializer implementation and you can use it to retrieve the original data types of transmited binary payload. To find it you can either:
- go through js source and look for classes with `deserializeBinary` method. One of them is likely the response class you are looking for
- or just go to the browser debugger again. There from the breakpoint you set to have a peek at the payload, just press `go over` button a couple of times and then you can find deserialze callback right in the local variables.

E.g `proto.grpc_web_scraper.ScrapeReply`

![reply_name](https://github.com/jacekciesielski/grpc-web-scraper/assets/111685433/4827b667-724b-4d96-bc35-95f0a833e350)

### 4. Note a flie containing js definitions.

You can easily check the file just by analysing html source or just by seeing stack trace of a request.

![stack_trace](https://github.com/jacekciesielski/grpc-web-scraper/assets/111685433/bfeb61f6-e119-45b4-8c4d-bc87bce38042)

### 5. Use the arguments to scrape the server

Finally that is the step we have all waited for! Just call the `scraper/scraper.py` script like that `python scraper/scraper.py --js-source-url file://playground/web-client/main.js --payload-int-array "0, 0, 0, 0, 5, 8, 128, 8, 16, 10" --response-name proto.grpc_web_scraper.ScrapeReply --scrape-url 'http://127.0.0.1:8080/grpc_web_scraper.Scrape/TryScraping'`

![response](https://github.com/jacekciesielski/grpc-web-scraper/assets/111685433/27fdbe61-645f-4a67-a51b-a2e7aef6934c)
