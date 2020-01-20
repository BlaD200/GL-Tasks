import firebase_admin
from firebase_admin import credentials, db

from os import getenv, environ
import json


def add_students_to_db(request) -> str:
    """
    Function to add students to Firebase Database
    :param request: Flask request that contains json with info about students:
    {
        "students": [
            {
              "student_id": 0,
              "firstName": "Brad",
              "lastName": "Rayburn",
              "release data": "2021.06.16",
              "university": "KNU"
            },
            ...
        ]
    }
    :return: str with json wrote to db or 'Bad request'
    """
    json_cred = {
        "type": getenv('type'),
        "project_id": getenv('project_id'),
        "private_key_id": getenv('private_key_id'),
        "private_key": getenv('private_key').replace('\\n', '\n'),
        "client_email": getenv('client_email'),
        "client_id": getenv('client_id'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": getenv('client_x509_cert_url')
    }

    cred = credentials.Certificate(json_cred)
    app = firebase_admin.initialize_app(cred, options={
        'databaseURL': 'https://vibrant-vector-260112.firebaseio.com/'
    })
    ref = db.reference('students', app)
    json_payload = request.get_json()
    if json_payload and 'students' in json_payload:
        for student in json_payload['students']:
            if ref.child(str(student['student_id'])):
                ref.child(str(student['student_id'])).update(student)
            else:
                ref.child(str(student['student_id'])).set(student)
        firebase_admin.delete_app(app)
        return 'Updated "students\\" db with following information:\n%s' % json_payload
    else:
        firebase_admin.delete_app(app)
        return 'Bad request'


##########################################################
def set_env(path_to_json_file: str):
    """
    Function to test code above in the local machine.
    Writes needed values to environmental variables.
    :param path_to_json_file: file with credentials in json
    """
    json_file = json.loads(open(path_to_json_file).read())
    for key in json_file:
        environ[key] = json_file[key]
##########################################################
