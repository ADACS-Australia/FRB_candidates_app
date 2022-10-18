from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator, InvalidPage
from django.core.serializers.json import DjangoJSONEncoder

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import models, serializers

import json
import requests
from decouple import config

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
    first_position = models.Position.objects.filter(frb=frb_event).order_by("-datetime").first()
    content = {
        "frb_event": frb_event,
        "first_position": first_position,
    }
    return render(request, 'cand_app/frbevent_details.html', content)


@api_view(['POST'])
def position_create(request):
    # Create frb event
    position = serializers.PositonSerializer(data=request.data)
    if position.is_valid():
        position.save()
        return JsonResponse({"data":position.data}, status=status.HTTP_201_CREATED)
    logger.debug(request.data)
    logger.error(position.errors)
    return Response(position.errors, status=status.HTTP_400_BAD_REQUEST)


def frbevent_table(request):
    # Grab events
    frb_events = models.FRBEvent.objects.all()
    frb_dict = list(frb_events.values())

    # Annotate the pointings for each event
    for frb in frb_dict:
        positions = models.Position.objects.filter(frb__id=frb["id"]).order_by('-datetime')
        frb["positions"] = list(positions.values())
        # Also add the most recent one to the main dict
        most_recent = list(positions.values())[0]
        frb["ra"] = most_recent["ra"]
        frb["dec"] = most_recent["dec"]
        frb["ra_hms"] = most_recent["ra_hms"]
        frb["dec_dms"] = most_recent["dec_dms"]
        frb["ra_pos_error"] = most_recent["ra_pos_error"]
        frb["dec_pos_error"] = most_recent["dec_pos_error"]
        frb["source"] = most_recent["source"]
        frb["datetime"] = most_recent["datetime"]


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
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"New FRB Event (ID:{frb_event.id})",
                }
            },
            {
                "type": "image",
                "title": {
                    "type": "plain_text",
                    "text": "FRB waterfall",
                },
                "image_url": "https://assets3.thrillist.com/v1/image/1682388/size/tl-horizontal_main.jpg",
                "alt_text": "marg"
            },
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
                        "action_id": "action_confirm"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Reject",
                        },
                        "style": "danger",
                        "action_id": "action_reject"
                    }
                ]
            }
        ]
    }
    headers = {'content-type': 'application/json'}
    r=requests.post(SLACK_WEBHOOK, data=json.dumps(slack_json), headers=headers)
    print(r.text)