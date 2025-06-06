## Overview

**Project Title**: File Transfer Server System

**Project Description**: A Client Server networking app that allows file transfers between computers

**Project Goals**:Enable reliable file transfer operations between computers and Support multiple client connections
## Instructions for Build and Use

Steps to build and/or run the software:

1. Ensure that Python is installed that is version 3.8 or higher
2. Download both server.py and client.py to the same folder

Instructions for using the software:

1. Open terminal and run "python server.py"
2. Open a second terminal and run "python client.py"
3. Available Client Commands:
- list - View all files available on the server
- download <filename> - Download a file from server to local directory
- upload <filepath> - Upload a local file to the server
- info - Display server information and capabilities
- help - Show detailed command usage
- quit - Exit the client application

## Development Environment 

To recreate the development environment, you need the following software and/or libraries with the specified versions:

* Python 3.8 or higher
* socket - TCP network communication
* threading - Concurrent client handling
* json - Message serialization/deserialization
* base64 - Binary file encoding for safe transfer
* os - File system operations
* datetime - File metadata timestamps

## Useful Websites to Learn More

I found these websites useful in developing this software:

* [Python Socket Programming](https://docs.python.org/3/library/socket.html)
* [Python Server Libraries](https://docs.python.org/3/library/socketserver.html)
* [What's the Difference Between TCP and UDP? - How-To Geek](https://www.howtogeek.com/190014/htg-explains-what-is-the-difference-between-tcp-and-udp/)
* [Python Threading Tutorial](https://docs.python.org/3/library/threading.html)
* [Client-Server Model - Wikipedia](https://en.wikipedia.org/wiki/Client%E2%80%93server_model)

## Future Work

The following items I plan to fix, improve, and/or add to this project in the future:

* [ ] Add a file compression system
* [ ] Allow folder transfers instead of just individual files
* [ ] Add an authentication system
