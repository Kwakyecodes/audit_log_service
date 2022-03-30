from flask import Flask, jsonify, request
from functools import wraps
from datetime import datetime

'''
This SQL returns a list of dictionary key value pairs of columns and rows
It also has flexible commands that make it easier to push and retrieve data from the sqlite database '''
from cs50 import SQL

app = Flask(__name__)

# Configure CS50 library to use SQLite database
db = SQL("sqlite:///log.db")

''' 
SCHEMA for log.db
CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, event_type TEXT NOT NULL);

CREATE TABLE data_logs (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, date TEXT NOT NULL, 
                        user TEXT NOT NULL, event TEXT NOT NULL, outcome TEXT DEFAULT 'Success', 
                        ip TEXT NOT NULL, error_msg TEXT DEFAULT null);

CREATE TABLE sqlite_sequence(name,seq); '''

# Token based authentication. Get token from json data
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        
        try:
            token = request.get_json()["token"]
        except:
            token = ''
            
        if not token:
            msg = jsonify(Error="Token is missing")
            return msg
        
        if token != "exampletoken":
            msg = jsonify(Error="Token is invalid")
            return msg
            
        return f(*args, **kwargs)
    
    return decorated


# This function takes the dictionary json object, and string new column as arguments and returns None
# The function adds a new column to the the data_logs table of db and inserts the data from the json object
def addColumn(json_data, column_name):
    value = json_data[column_name]
    
    # Add new column
    if type(value) == int:
        db.execute(f"ALTER TABLE data_logs ADD {column_name} INTEGER DEFAULT ?", 0)
    elif type(value) == str:
        db.execute(f"ALTER TABLE data_logs ADD {column_name} TEXT DEFAULT null")
    elif type(value) == float:
        db.execute(f"ALTER TABLE data_logs ADD {column_name} NUMERIC DEFAULT ?", 0)
            
    # TODO: Catch non int, non str and non float values of value
    
    # Insert value of new column for current log
    id = db.execute("SELECT id FROM data_logs")[-1]["id"]
    db.execute(f"UPDATE data_logs SET {column_name} = ? WHERE id = ?", value, id)
    
    return
        

# This function takes string event as arguments and returns None. 
# The function adds the new event to the events table of db
def addEvent(event):
    db.execute("INSERT INTO events (event_type) VALUES(?)", event)
    return


# This function takes dictionary json_data and string ip and returns None. 
# The function inserts common data to data_logs table of db
def insertCommons(json_data, ip):
    date = f"{datetime.now()}"

    db.execute("INSERT INTO data_logs (date, user, event, outcome, ip, error_msg) VALUES (?,?,?,?,?,?)", 
               date, json_data["user"], json_data["event"], json_data["outcome"], ip, json_data["error_msg"])
    return


# This function takes a dictionary item and a dictionary condition and returns a list of dictionaries
# The function then SELECT item from data_logs table WHERE condition
def select(item, condition):
    # TODO: Complete this function
    return result
    

'''
This functions receives a json object with the information for the data_logs table via a POST request with the url /log, 
logs the information unto the database and returns a json message, which gives feedback about the request. '''
@app.route("/log", methods=["POST"])
@token_required
def log():
    # TODO: Use try and except to catch all possible errors
    
    if request.method == "POST":
        json_dict = request.get_json()
        
        # Check if event has been logged before
        event = json_dict["event"]
        existing_events = [row["event_type"] for row in db.execute("SELECT event_type FROM events")]
        isNewEvent = not event in existing_events
        
        
        COMMON_DATA = ["date", "user", "event", "outcome", "ip", "error_msg"]
        try:
            EXISTING_DATA = [col for col in db.execute("SELECT * FROM data_logs")[0]]
        except:
            EXISTING_DATA = []
        
        # Add new event to events table of db and create new columns for event specific data in data_logs of db
        if isNewEvent:
            addEvent(event=event)
            insertCommons(json_data=json_dict, ip=f"{request.remote_addr}")
            
            for data in json_dict:
                if data not in (COMMON_DATA + EXISTING_DATA) and data != "token":
                    addColumn(json_data=json_dict, column_name=data)
                    
        # Insert common and event specific data for event that has been logged before      
        else:
            insertCommons(json_data=json_dict, ip=f"{request.remote_addr}")
            
            for data in json_dict:
                if data not in (COMMON_DATA + EXISTING_DATA) and data != "token":
                    id = db.execute("SELECT id FROM data_logs")[-1]["id"]
                    db.execute(f"UPDATE data_logs SET {data} = ? WHERE id = ?", json_dict[data], id)
                    
        msg = jsonify(Success="Data logged successfully")
        return msg


'''
This function accepts a get request via the url /query and then returns a json object containing all the
data in the table data_logs in db. It essentially returns all the data from the audit log service. '''
@app.route("/query", methods=["POST"])
@token_required
def query():
    # TODO: Use select function to perform query via a POST request
    if request.method == "POST":
        all_data = db.execute("SELECT * FROM data_logs")
        result = jsonify(all_data)
        return result
    
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000)