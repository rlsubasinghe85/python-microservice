import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util


server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://localhost:27017/videos"

#rabbitmq_params = pika.ConnectionParameters{
#    host='rabbitmq',
#    port=5672
#}

mongo = PyMongo(server)
#Establish a connection to RabbitMQ
connection=pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
#Create a channel
channel = connection.channel()

#Declare a queue (Create it if doesn't exist)
channel.queue_declare(queue='video')

@server.route("/login", methods=["POST"])
def login():
    print(request)
    token, err = access.login(request)
    print(token)
    if not err:
        return token
    else:
        return err

@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)
    access = json.loads(access)

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file is required", 400
        for _, f in request.files.items:
           err = util.upload(f, fs, channel, access)
           if err:
               return err
        return "Success!", 200
    else:
        return "Not Authorized", 401

@server.route("/download", methods=["GET"])
def download():
    pass

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
