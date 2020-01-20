import base64

# pip install google-cloud-pubsub==1.1.0
from google.cloud import pubsub_v1

import os
import requests


def fan_out(request):
    """
    Responds to any HTTP request with 'url_to_file' parameter, then post each line of file to `TOPIC_NAME` topic
    of google cloud pub/sub
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    if list(request.args.keys()):
        parameters = request.args
    else:
        parameters = request.get_json()

    url_to_file = parameters.get('url_to_file', None)

    if url_to_file:
        content = requests.get(url_to_file).content.decode()

        publisher = pubsub_v1.PublisherClient()
        topic_name = 'projects/{project_id}/topics/{topic}'.format(
            project_id=os.getenv('GOOGLE_CLOUD_PROJECT_ID'),
            topic=os.getenv('TOPIC_NAME')
        )

        for line in content.split('\n'):
            publisher.publish(topic_name, line.encode('utf-8'))
            # encode is used because messages posting to pub/sub must be in byte strings

        return 'Publishing succeeded'
    return 'Publishing failed'


def sub_print(event, context):
    """
    Triggered from a message on a Cloud Pub/Sub topic and print it.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print("Message id: {} [{}] : {} | {}".format(context.event_id, context.timestamp, context.resource, pubsub_message))
