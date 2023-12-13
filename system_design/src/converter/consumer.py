import pika, sys, os, time
from pymongo import MongoClient
import gridfs
from convert import to_mp3


def main():
    client = MongoClient("host.minikube.internal", 27017)
    db_videos = client.videos
    db_mp3s = client.mp3

    # Declare the gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3 = gridfs.GridFS(db_mp3s)

    # Connect to the RabbitMQ Server
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    # Declare the callback function
    def callback(ch, method, properties, body):
        print(f"Received message: {body.decode()}")
        err = to_mp3.start(body, fs_videos, fs_mp3, ch)

        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basick_ack(delivery_tag=method.delivery_tag)

    # Set up the callback function to process video messages
    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

# Start the main function
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    finally:
        print("Exiting Program.")
