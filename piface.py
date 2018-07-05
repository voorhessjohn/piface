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

#-----------------------------------------------------------------
# function: adds timestamp to response and converts a list of 
#           responses to formatted rows in csv. Uses Pandas to
#           separate each emotion into its own row with a boolean
#           value.
# parameters: responses_list (list) - list of responses returned by
#                                     detect_all_faces_in_bucket()
#             file_name (string) - the name of the file to be saved
# returns: nothing
#-----------------------------------------------------------------
def write_formatted_csv_from_list_of_responses(responses_list, file_name):
    rows = []
    with open(file_name, 'w') as f:     
        for response in responses_list:
            for face in response['FaceDetails']:
                face_dict = {}
                face_dict['time'] = time.time()
                if face['Sunglasses']['Value'] == True:
                    face_dict['Sunglasses'] = 1
                else:
                    face_dict['Sunglasses'] = 0
                if face['Sunglasses']['Confidence'] > 0:
                    face_dict['Sunglasses_Confidence'] = face['Sunglasses']['Confidence']
                else:
                    face_dict['Sunglasses_Confidence'] = 0
                face_dict['Gender'] = face['Gender']['Value']
                if face['Gender']['Confidence'] > 0:
                    face_dict['Gender_Confidence'] = face['Gender']['Confidence']
                else:
                    face_dict['Gender_Confidence'] = 0
                if face['EyesOpen']['Value'] == True:
                    face_dict['EyesOpen'] = 1
                else:
                    face_dict['EyesOpen'] = 0
                if face['EyesOpen']['Confidence'] > 0:
                    face_dict['EyesOpen_Confidence'] = face['EyesOpen']['Confidence']
                else:
                    face_dict['EyesOpen_Confidence'] = 0
                if face['Beard']['Value'] == True:
                    face_dict['Beard'] = 1
                else:
                    face_dict['Beard'] = 0
                if face['Beard']['Confidence'] > 0:
                    face_dict['Beard_Confidence'] = face['Beard']['Confidence']
                else:
                    face_dict['Beard_Confidence'] = 0
                face_dict['Pose_Pitch'] = face['Pose']['Pitch']
                face_dict['Pose_Yaw'] = face['Pose']['Yaw']
                face_dict['Pose_Roll'] = face['Pose']['Roll']
                face_dict['Emotions'] = face['Emotions']
                for emotion in face_dict['Emotions']:
                    emotion_type = emotion['Type']
                    face_dict[emotion_type] = 1
                    face_dict['Confidence_'+emotion_type] = emotion['Confidence']
                face_dict['Feelings'] = face['Emotions'][0]['Type']
                face_dict['Emotion_1'] = face['Emotions'][0]['Type']
                face_dict['Emotion_2'] = face['Emotions'][1]['Type']
                face_dict['Emotion_3'] = face['Emotions'][2]['Type']
                face_dict['Confidence_1'] = face['Emotions'][0]['Confidence']
                face_dict['Confidence_2'] = face['Emotions'][1]['Confidence']
                face_dict['Confidence_3'] = face['Emotions'][2]['Confidence']


                rows.append(face_dict)
    df = pd.DataFrame(rows)
    df.fillna(value = '0', inplace=True)
    df.to_csv(file_name)


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


