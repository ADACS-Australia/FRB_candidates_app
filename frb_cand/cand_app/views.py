from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, InvalidPage
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import models, serializers

import json
import requests
from decouple import config
import time

import logging
logger = logging.getLogger(__name__)

SLACK_WEBHOOK=config("SLACK_WEBHOOK")

def home_page(request):
    return render(request, 'cand_app/home_page.html')


@api_view(['POST'])
def frbevent_create(request):
    # Create frb event
    frb_cand = serializers.FRBEventSerializer(data=request.data)
    search_file = request.data.get("search_open")
    image_file = request.data.get("image_open")
    histogram_file = request.data.get("histogram_open")
    if frb_cand.is_valid():
        if search_file is None:
            return Response(
                "Missing search file", status=status.HTTP_400_BAD_REQUEST
            )
        if image_file is None:
            return Response(
                "Missing image file", status=status.HTTP_400_BAD_REQUEST
            )
        if histogram_file is None:
            return Response(
                "Missing histogram file", status=status.HTTP_400_BAD_REQUEST
            )
        frb_cand.save(
            search_path=search_file,
            image_path=image_file,
            histogram_path=histogram_file,
        )
        return JsonResponse({"data":frb_cand.data, "id":frb_cand.data["id"]}, status=status.HTTP_201_CREATED)
    logger.debug(request.data)
    logger.error(frb_cand.errors)
    return Response(frb_cand.errors, status=status.HTTP_400_BAD_REQUEST)


def frbevent_details(request, id):
    frb_event = models.FRBEvent.objects.get(id=id)
    radio_measurements = models.RadioMeasurement.objects.filter(frb=frb_event).order_by("-datetime")
    frb_ratings = models.EventRating.objects.filter(frb=frb_event)
    ratings = {
        "pos_rates": len(frb_ratings.filter(rating=True)),
        "neg_rates": len(frb_ratings.filter(rating=False)),
    }
    content = {
        "frb_event": frb_event,
        "first_radio_measurement": radio_measurements.first(),
        "radio_measurements": radio_measurements,
        "ratings": ratings,
    }
    return render(request, 'cand_app/frbevent_details.html', content)


@api_view(['POST'])
def radio_measurement_create(request):
    # Create frb event
    radio_measurement = serializers.RadioMeasurementSerializer(data=request.data)
    if radio_measurement.is_valid():
        radio_measurement.save()
        return JsonResponse({"data":radio_measurement.data}, status=status.HTTP_201_CREATED)
    logger.debug(request.data)
    logger.error(radio_measurement.errors)
    return Response(radio_measurement.errors, status=status.HTTP_400_BAD_REQUEST)


def frbevent_table(request):
    # Grab events
    frb_events = models.FRBEvent.objects.all()
    frb_dict = list(frb_events.values())

    # Annotate the pointings for each event
    for frb in frb_dict:
        radio_measurements = models.RadioMeasurement.objects.filter(frb__id=frb["id"]).order_by('-datetime')
        frb["radio_measurements"] = list(radio_measurements.values())
        # Count ratings
        ratings = models.EventRating.objects.filter(frb__id=frb["id"])
        frb["pos_rates"] = len(ratings.filter(rating=True))
        frb["neg_rates"] = len(ratings.filter(rating=False))
        if len(list(radio_measurements.values())) > 0:
            # Also add the most recent one to the main dict
            most_recent = list(radio_measurements.values())[0]
            for rmkey in most_recent.keys():
                if rmkey == "id":
                    # Skip measurement ID so it doesn't overide frb ID
                    continue
                frb[rmkey] = most_recent[rmkey]
            # Grab the display name for source
            frb["source"] = dict(models.POS_SOURCE_CHOICES)[most_recent["source"]]


    # Convert to json
    frb_json = json.dumps(frb_dict, cls=DjangoJSONEncoder)

    content = {
        "frb_json": frb_json,
    }
    return render(request, 'cand_app/frbevent_table.html', content)


def slack_event_post(id):
    frb_event = models.FRBEvent.objects.get(id=id)
    slack_json = {
        "blocks": [
            # Title
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"New FRB Event (ID:{frb_event.id})",
                }
            },
            # The detection images
            {
                "type": "image",
                "title": {
                    "type": "plain_text",
                    "text": "FRB search",
                },
                "image_url": f"{settings.PRODUCTION_URL}{frb_event.search_path.url}",
                "alt_text": "search"
            },
            {
                "type": "image",
                "title": {
                    "type": "plain_text",
                    "text": "FRB radio image",
                },
                "image_url": f"{settings.PRODUCTION_URL}{frb_event.image_path.url}",
                "alt_text": "image"
            },
            {
                "type": "image",
                "title": {
                    "type": "plain_text",
                    "text": "FRB histogram",
                },
                "image_url": f"{settings.PRODUCTION_URL}{frb_event.histogram_path.url}",
                "alt_text": "histogram"
            },
            # Response buttons
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Confirm",
                        },
                        "style": "primary",
                        "action_id": "action_confirm",
                        "value" : f"{frb_event.id}",
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Reject",
                        },
                        "style": "danger",
                        "action_id": "action_reject",
                        "value" : f"{frb_event.id}",
                    }
                ]
            }
        ]
    }
    headers = {'content-type': 'application/json'}
    r=requests.post(SLACK_WEBHOOK, data=json.dumps(slack_json), headers=headers)
    print(r.text)


@api_view(['POST'])
def slack_get_rating(request):
    # Load slack payload
    data = json.loads(request.data.dict()["payload"])
    logger.debug(json.dumps(data, indent=4))

    action = data["actions"][0]["action_id"]
    frb_id = data["actions"][0]["value"]
    logger.debug(f'action: {action}')
    logger.debug(f'frb_id: {frb_id}')
    frb_event = models.FRBEvent.objects.get(id=frb_id)

    slack_id = data["user"]["id"]
    slack_username = data["user"]["username"]
    logger.debug(f'id: {slack_id}')
    logger.debug(f'user: {slack_username}')

    # Get or create slack user
    slack_user = models.SlackUser.objects.get_or_create(
        id=slack_id,
        defaults={
            "name": slack_username,
        },
    )[0]

    # Record their rating
    event_rating = models.EventRating.objects.get_or_create(
        frb=frb_event,
        user=slack_user,
    )[0]
    if action == 'action_confirm':
        event_rating.rating = True
    else:
        event_rating.rating = False
    event_rating.save()


    # Record response in thread
    headers = {'content-type': 'application/json'}
    response_json = json.dumps(
        {
            "thread_ts": data["container"]["message_ts"],
            "channel": data["container"]["channel_id"],
            "text": f"{slack_username}'s {action.split('_')[1]} classification has been recorded.",
        }
    )
    r = requests.post(SLACK_WEBHOOK, data=response_json, headers=headers)
    logger.debug(r)

    # Acknowldege repsonse
    return HttpResponse(headers=headers)


def ask_for_tns_reply(id_report):
    reply_url = settings.TNS_URL + "/bulk-report-reply"
    headers = {'User-Agent': f'tns_marker{{"tns_id": "{settings.TNS_BOT_ID}", "type": "bot", "name": "{settings.TNS_BOT_NAME}"}}'}
    reply_data = {'api_key': settings.TNS_API_KEY, 'report_id': id_report}
    response = requests.post(reply_url, headers=headers, data=reply_data)
    return response


def submit_frb_to_tns(id):
    # Grab frb and radio_measurement
    frb_event = models.FRBEvent.objects.get(id=id)
    radio_measurement = models.RadioMeasurement.objects.filter(frb__id=id).first()

    # Prepare data to upload to TNS
    print(f"Sending FRB {id} to the TNS...\n")
    json_url = settings.TNS_URL + "/bulk-report"
    headers = {'User-Agent': f'tns_marker{{"tns_id": "{settings.TNS_BOT_ID}", "type": "bot", "name": "{settings.TNS_BOT_NAME}"}}'}
    frb_dict = {
        "frb_report": {
            "0": {
                "ra": {
                    "value": radio_measurement.ra,
                    "error": radio_measurement.ra_pos_error,
                    "units": "deg"
                },
                "dec": {
                    "value": radio_measurement.dec,
                    "error": radio_measurement.dec_pos_error,
                    "units": "deg"
                },
                "discovery_datetime": frb_event.time_of_arrival.replace(tzinfo=None).isoformat(' '),
                "internal_name": "CRAFT",
                "dm": radio_measurement.dm,
                "dm_err": radio_measurement.dm_err,
                "reporting_group_id": 58, #CRAFT
                "discovery_data_source_id": 58, #CRAFT
                "photometry": {
                    "photometry_group": {
                        "0": {
                            "obsdate": frb_event.time_of_arrival.replace(tzinfo=None).isoformat(' '),
                            #TODO need real values for these too
                            "flux": radio_measurement.flux,
                            "flux_error": radio_measurement.flux_err,
                            "flux_units": 8,
                            "filter_value": 1,
                            "instrument_value": 1,
                            "snr": radio_measurement.sn,
                            "ref_freq": 1271.5,
                            "inst_bandwidth": 336,
                            "channels_no": 336,
                            "sampling_time": 1.182,
                        }
                    }
                }
                # "related_files": {
                #     "0": {
                #     "related_file_name": "rel_file_1.png",
                #     "related_file_comments": ""
                #     },
                #     "1": {
                #     "related_file_name": "rel_file_2.jpg",
                #     "related_file_comments": ""
                #     }
                # }
            }
        }
    }
    json_read = json.dumps(frb_dict, indent = 4)
    logger.debug(f"json_read:{json_read}")
    json_data = {'api_key': settings.TNS_API_KEY, 'data': json_read}
    response = requests.post(json_url, headers=headers, data=json_data)
    if response.status_code == 200:
        print("The report was sent to the TNS.\n")
        json_data = response.json()
        id_report = json_data['data']['report_id']
        print(f"Report ID = {id_report}\n")
    else:
        print(f"{response.status_code}: The report was not sent to the TNS.\n")
        print(response.reason)
        return None

    # Get reply from the TNS about the objname given
    sleep_sec = 2
    timeout = 30
    print(f"Sending reply for the report id {id_report} ...\n")
    time.sleep(sleep_sec)
    response = ask_for_tns_reply(id_report)
    counter = sleep_sec
    while True:
        if (response.status_code == 404) and (counter <= timeout):
            time.sleep(sleep_sec)
            response = ask_for_tns_reply(id_report)
            counter = counter + sleep_sec
        else:
            break
    try:
        objname = response.json()['data']['feedback']["frb_report"][0]["100"]["objname"]
    except Exception as e:
        print(e)
        print(f"response json:\n{json.dumps(response.json(), indent = 4)}\n")
        return None
    else:
        return objname


def trigger_pipeline(request, id):
    #TODO will sent off request here, maybe output where it will output data

    #TODO only admins should be able to click this
    # Return to confirmation page
    return render(request, 'cand_app/trigger_pipeline.html')