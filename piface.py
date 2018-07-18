import time
import boto3
from picamera import PiCamera
import turtle
from turtle import Turtle, Screen
import os
import sys

emotion_dict = {}
conf_dict = {}
camera = PiCamera()
camera.resolution = (640, 480)
count = 0
count2 = 0
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
response_list = []
timestamp_list = []


# -----------------------------------------------------------------
# function: adds timestamp to response and converts a list of
#           responses to formatted rows in csv. Uses Pandas to
#           separate each emotion into its own row with a boolean
#           value.
# parameters: responses_list (list) - list of responses returned by
#                                     detect_all_faces_in_bucket()
#             file_name (string) - the name of the file to be saved
# returns: nothing
# -----------------------------------------------------------------
def write_formatted_csv_from_list_of_responses(responses_list, file_name):
    rows = []
    with open(file_name, 'w') as f:
        i = 0
        for response in responses_list:
            for face in response['FaceDetails']:
                face_dict = {}
                face_dict['time'] = timestamp_list[i]
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
                    face_dict['Confidence_' + emotion_type] = emotion['Confidence']
                face_dict['Feelings'] = face['Emotions'][0]['Type']
                face_dict['Emotion_1'] = face['Emotions'][0]['Type']
                face_dict['Emotion_2'] = face['Emotions'][1]['Type']
                face_dict['Emotion_3'] = face['Emotions'][2]['Type']
                face_dict['Confidence_1'] = face['Emotions'][0]['Confidence']
                face_dict['Confidence_2'] = face['Emotions'][1]['Confidence']
                face_dict['Confidence_3'] = face['Emotions'][2]['Confidence']

                rows.append(face_dict)
        i += 1
    df = pd.DataFrame(rows)
    df.fillna(value='0', inplace=True)
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
    camera.capture(image)
    timestamp_list.append(time.time())
    return image


# function to run aws detect_faces function on picture
# and returns response that holds all attributes
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

    mood = str((response['FaceDetails'][0]['Emotions'][0]['Type']))
    mood2 = str((response['FaceDetails'][0]['Emotions'][1]['Type']))
    mood3 = str((response['FaceDetails'][0]['Emotions'][2]['Type']))

    # if mood in emotion_dict.keys():
    #     emotion_dict[mood] += 1
    # else:
    #     emotion_dict[mood] = 1

    confidence1 = (response['FaceDetails'][0]['Emotions'][0]['Confidence'])
    confidence2 = (response['FaceDetails'][0]['Emotions'][1]['Confidence'])
    confidence3 = (response['FaceDetails'][0]['Emotions'][2]['Confidence'])

    if mood in conf_dict.keys():
        conf_dict[mood] += int(confidence1)
    else:
        conf_dict[mood] = int(confidence1)

    if mood2 in conf_dict.keys():
        conf_dict[mood2] += int(confidence2)
    else:
        conf_dict[mood2] = int(confidence2)

    if mood3 in conf_dict.keys():
        conf_dict[mood3] += int(confidence3)
    else:
        conf_dict[mood3] = int(confidence3)

    return response


def upload_pic(filepath, bucket):
    data = open(filepath, 'rb')
    s3.Bucket(bucket).put_object(Key=filepath, Body=data)
    return bucket, filepath


# function that generates the mood and confidence
# in text in the center of a box filled with the
# color code for the respective mood using turtle
def show_mood(mood, confidence):
    font = ("Arial", 14, "bold")
    color = MOOD_COLORS[mood]
    t.begin_fill()
    t.pencolor('white')
    t.hideturtle()
    t.fillcolor(color)
    t.up()
    t.goto(-100, -100)
    t.down()
    for i in range(4):
        t.forward(200)
        t._rotate(90)
    t.end_fill()
    t.up()
    t.home()
    t.pencolor('black')
    t.write(mood + ': \n', align='center', font=font)
    t.write("{0}%".format(round(confidence)), align='center', font=font)


def parse_mood(response):
    if not response['FaceDetails']:
        return (0,0)
    else:
        mood = response['FaceDetails'][0]['Emotions'][0]['Type']
        confidence = response['FaceDetails'][0]['Emotions'][0]['Confidence']
    return mood, confidence


# function that prints average mood
def avg_emotion():
    # most_often = sorted(emotion_dict.items(), key=lambda x: x[1], reverse=True)[0]
    # print('Overall the customer is {}.'.format(most_often[0]))

    most_conf = sorted(conf_dict.items(), key=lambda x: x[1], reverse=True)[0]
    print('Overall the customer is {}'.format(most_conf[0]))
#    print('Total confidence = {}%.'.format(most_conf[1]))


# main menu
def menu():
    global count
    global count2

    if count == 0:
        os.system('clear')
        print('                    ___  ___  ____     ____      ____        ______')
        print('                   /   |/   |/    /   /  _ \    /  _ \      /  _   \ ')
        print('                  /              /   |  | | |  |  | | |    /  / /  /')
        print('                 /    /|___/    /    |  |_| |  |  |_| |   /  /_/  /')
        print('                /____/     /___/      \____/    \____/   /_______/')
        print('    _____     _____  ____  ___    ____    __  ___  _____ ______ _____ ___     __  ___')
        print('   /  __ \   / ___/ / ___// _ \  / ___\  /  |/  / /_  _//_  __//_  _// _ \   /  |/  /')
        print('  /  /_/_/  / /_   / /   | | | || /____ /      /   / /   / /    / / | | | | /      /')
        print(' /  /\  \  /  _/_ / /__  | |_| || |_/ //      / __/ /_  / /  __/ /_ | |_| |/      /')
        print('/__/  \__|/_____//____/   \___/ \____//__/|__/ /_____/ /_/  /_____/  \___//__/|__/')
        print('                    _________    ________     ___  ___  ____')
        print('                   /__   ___/   /__  ___/    /   |/   |/    /')
        print('                     /   /        /  /      /              /')
        print('                  __/   /__      /  /      /    /|___/    /')
        print('                 /________/     /__/      /____/     /___/')
        time.sleep(5)
    count += 1
    os.system('clear')
    menu_login = input('  ---Main Menu---\n\n     1: Login\n     '
                       '2. Exit\n\n' 'Enter Input: ')

    if menu_login == '1':
        while logged_in == False:
            try:
                os.system('clear')
                print('--Login--\n')
                username = input('Username: ')
                password = input('Password: ')
                log_in(username, password)
                try:
                    while True:

                        os.system('clear')
                        print('Demo ITM currently in use...\n\n')
                        print('Enter Cntrl-c to end session')

                        while logged_in == True:
                            image = take_picture()
                            upload = upload_pic(image, 'teamofdestinygenesis')
                            detect = detect_faces(upload[0], upload[1])
                            response_list.append[detect]
                            conf_tup = parse_mood(detect)
                            if conf_tup[0] != 0:
                                show_mood(conf_tup[0],conf_tup[1])
                            else:
                                pass
                            count2 += 1
                            if count2 % 5 == 0:
                                avg_emotion()

                except KeyboardInterrupt as k:
                    print(k)
                    break

            except:
                print('\nInvalid username or password...Please try again\n\n')
                time.sleep(3)

    elif menu_login == '2':
        sys.exit()

    else:
        print('Invalid Command. Please try again...')
        time.sleep(3)
        menu()


# main
try:
    while True:
        menu()
except KeyboardInterrupt:
    menu()


