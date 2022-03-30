# audit_log_service
audit_log_service is a simple python API created with the Flask. The API has only two routes: /log and /query. 
Both accept only post requests and json data. To access these routes, you will need authentication: this is done by passing a
token via the json block. /log saves json object into a sqlite database and /query retrieves data stored inside the database.
Due to time issues, other functionalities of CRUD, such as Update and Delete could not be added.

## Deploying Flask app on Ubuntu
* Create user. For this example, I'll name the user "emma"
```
$ adduser emma
```
* Insert password and password confirmation as you like.
* Update software packages in Ubuntu server first to ensure you can install python3 and other packages you are going to need:
```
$ apt update
```
* first install web server Nginx:
```
$ apt install nginx
```
* now create a configuration file for your Nginx:
```
nano /etc/nginx/sites-enabled/flask_app
```
* inside the editor add code as follow:
```
server {
    listen 80;
    server_name 192.0.2.0;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
* Disable Nginx default configuration since you are going to use your own configuration:
```
unlink /etc/nginx/sites-enabled/default
```
* Reload Nginx server using command:
```
nginx -s reload
```
* next, install python3:
```
apt install python3
```
* install python3 pip
```
$ apt install python3-pip
```
* then navigate to created user’s home directory (in my case, the user I created is “emma”)
```
$ cd /home/emma
```
* Install flask
* Download flask app from github repository
* test server by typing 
```
$ python3 __init__.py
```
* Now install Gunicorn:
```
$ apt install gunicorn3
```
* Run Gunicorn from your application’s root directory (inside myproject NOT inside application)
```
$ gunicorn3 --workers=3 application:app
```
* Now the flask application is live over the internet and you can access it directly using your domain or IP address.



## Testing with CURL
### Logging data into the database
* Route: /log
* Token: exampletoken
* method: POST request
* accepts only json data.
* CURL command to send a POST request to /log:

```bash
curl -X POST http://localhost:5000/log
   -H 'Content-Type: application/json'
   -d '{"token":"exampletoken","user":"user_name","event":"name_of_event", "outcome":"the_outcome", "error_msg":"error"}'
``` 
* The items in the json data are the common data. Additional items(event specific data) can be added to the json data during in the post request.
* Running the CURL command above should return:

```
{
"Success": "Data logged successfully"
}
```

### Querying data from the database
* Route: /query
* Token: exampletoken
* method: POST request
* accepts only json data.
* CURL command to send a POST request to /query:

```bash
curl -X POST http://localhost:5000/query
   -H 'Content-Type: application/json'
   -d '{"token":"exampletoken"}'
```

* Running the command above should return a json object of all the files in the database. Because there is not data in the database, it currently returns:

```
[]
```

