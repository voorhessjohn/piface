import time
import boto3
#import picamera
import turtle
from turtle import Turtle, Screen
s = Screen()
t = turtle.Turtle()
s.setup(200, 200)
s3 = boto3.resource('s3')
client = boto3.client('rekognition')
USER_PASS_DICT = {'admin': 'admin'}
MOOD_COLORS = {'HAPPY': 'green', 'SAD': 'blue', 'ANGRY': 'red',
               'CONFUSED': 'yellow', 'DISGUSTED': 'brown', 'UNKNOWN': 'white',
               'CALM': 'pink'}
logged_in = False


def log_in(username, password):
    global logged_in
    if password == USER_PASS_DICT[username]:
        logged_in = True
    else:
        logged_in = False


def log_out():
    global logged_in
    logged_in = False


def take_picture():
    image = 'image' + str(time.time()) + '.jpg'
    #camera.capture(image)
    return image


def detect_faces(bucket, name):
    response = client.detect_faces(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': name
            }
        },
        Attributes=['ALL']
    )
    return response


def upload_pic(filepath, bucket):
    data = open(filepath, 'rb')
    s3.Bucket(bucket).put_object(Key=filepath, Body=data)


def show_mood(mood, confidence):
    color = MOOD_COLORS[mood]
    t.begin_fill()
    t.pencolor('white')
    #t.setfillopacity(confidence)
    t.hideturtle()
    t.fillcolor(color)
    t.up()
    t.forward(100)
    t._rotate(90)
    t.forward(100)
    t.down()
    t._rotate(90)
    t.forward(200)
    t._rotate(90)
    t.forward(200)
    t._rotate(90)
    t.forward(200)
    t._rotate(90)
    t.forward(200)
    t.up()
    t._rotate(90)
    t.forward(100)
    t._rotate(90)
    t.forward(100)
    t.end_fill()
    time.sleep(3)


def parse_mood(response):
    mood = response['FaceDetails'][0]['Emotions'][0]['Type']
    confidence = response['FaceDetails'][0]['Emotions'][0]['Confidence']
    return mood, confidence


names = ['courtney_sad.jpg', 'dan_happy.jpg', 'fontana.jpg', 'tim_serious.jpg']


while logged_in:
    conf_tup = parse_mood((detect_faces('moodrecognition', take_picture())))
    show_mood(conf_tup[0],conf_tup[1])
    time.sleep(2)


