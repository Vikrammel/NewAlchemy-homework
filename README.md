# Single-Site File Store in Python
### by Vikram Melkote

A single-server datastore that stores files for multiple users via user registration and session management

Specifications: https://github.com/newalchemylimited/homework/wiki/Assignment:-Simple-storage-server

### Setup

#### Running using Docker (preferred):

- install docker from [here](https://docs.docker.com/install/ "link to docker install guide")

- navigate to project directory in terminal

- build docker image: `docker build -t data_store .`

- run image: `docker run -p 5000:5000 data_store`

#### Running on local machine:

- If on Windows: cURL comes pre-installed on macOS and Linux. For windows download the .zip from [here](https://curl.haxx.se/download.html "link to cURL download") then unzip the archine in a directory of your choice to use cURL.

- Install python3/pip3 if not installed from [here](http://docs.python-guide.org/en/latest/starting/installation/ "link to python3 download").

- open terminal in project root folder and run `pip3 install -r requirements.txt`

- run `python3 DataStore.py` from project root directory



### Usage:

#### cURL:

Open Terminal.


- Register User:

`curl --request POST --data "{'username':'<username>','password':'<password>'}"   http://localhost:5000/register`


- User Login:

`curl --request POST --data "{'username':'<username>','password':'<password>'}"   http://localhost:5000/login`


- User Logout:

`curl --request POST --header "X-Session: <token returned from previous /login request>"   http://localhost:5000/logout`


- User PUT file:

`cd` into directory that contains <filename> from terminal (include file extension in \<filename>)

`curl --header "X-Session: <token returned from previous /login request>" --header "Content-Length: <length of file as string>"  --header "Content-Type: <type of content as text eg. 'text/html'>" --request PUT --data "@<filename>"   http://localhost:5000/files/<filename>`


- User GET file:

`curl --header "X-Session: <token returned from previous /login request>" --request GET http://localhost:5000/files/<filename>`


- User GET all files:

`curl --header "X-Session: <token returned from previous /login request>" --request GET http://localhost:5000/files`


- User DELETE file:

`curl --header "X-Session: <token returned from previous /login request>" --request DELETE http://localhost:5000/files/<filename>`
