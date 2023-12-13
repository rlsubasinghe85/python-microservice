import os, requests
import json, pika

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
    except Exception as err:
        print(f'upload : {err}' )
        return "Internal Server Error {err}", 500

    message = {
        "video_fid": fid,
        "mp3_fid": None,
        "username": access["username"]
    }

    #create the queue and try to put the message
    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except:
        fs.delete(fid)
        return "Internal Server Error", 500
        
