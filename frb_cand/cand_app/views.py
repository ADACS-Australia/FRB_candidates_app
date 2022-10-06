from django.shortcuts import render
from django.db import transaction

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import models, serializers

import logging
logger = logging.getLogger(__name__)


@api_view(['POST'])
@transaction.atomic
def frbevent_create(request):
    # Create frb event
    frb_cand = serializers.FRBEventSerializer(data=request.data)
    search_file = request.data.get("search_open")
    image_file = request.data.get("image_open")
    histogram_file = request.data.get("histogram_open")
    print(search_file, image_file, histogram_file)
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
        return Response(frb_cand.data, status=status.HTTP_201_CREATED)
    logger.debug(request.data)
    logger.error(frb_cand.errors)
    return Response(frb_cand.errors, status=status.HTTP_400_BAD_REQUEST)
