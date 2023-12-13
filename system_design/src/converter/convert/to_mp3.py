import pika, json, tempfile, os
from bson.objectid import ObjectId
import moviepy.editor


def start(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message)
    print(f"consumer -> body: {message}")

    # Create the temporary file
    tf = tempfile.NamedTemporaryFile()

    # Get the video content
    out = fs_videos.get(message['video_fid'])
    tf.write(out.read())

    # Add video content to empty file
    audio = moviepy.editor.VideoFileClip(tf.name).audio
    tf.close()

    # Write the audio to file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)

    #  Save file to MongoDB
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    os.remove(tf_path)

    print(f"mp3 file_id: {fid}")
    message["mp3_fid"] = str(fid)

    # Publish to MP3 queue
    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )   
    except Exception as err:
        fs_mp3s.delete(fid)
        return "Failed to publish message."
