#!/usr/bin/env python

import os
import glob
import argparse
import urllib.request
import requests
import json
import yaml

from astropy.coordinates import Angle
import astropy.units as u
from astropy.io import fits

import logging
logger = logging.getLogger(__name__)

# SYSTEM_ENV = os.environ.get('SYSTEM_ENV', None)
# if SYSTEM_ENV == 'DEVELOPMENT':
#     BASE_URL = 'http://127.0.0.1:8000'
# else:
#     BASE_URL = 'https://mwa-image-plane.duckdns.org'
BASE_URL = 'http://127.0.0.1:8000'


class TokenAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = "Token {}".format(self.token)
        return r



def frbevent_upload(yaml_path):
    """ Upload an MWA observation to the database.

    Parameters
    ----------
    obsid : `int`
        MWA observation ID.
    """

    # Upload
    session = requests.session()
    session.auth = session.auth = (os.environ['FRB_USER'], os.environ['FRB_PASS'])
    url = f'{BASE_URL}/frbevent_create/'

    with open(yaml_path, 'r') as file:
        frb_dict = yaml.safe_load(file)
    data = {
        "tns_name": frb_dict["tns_name"],
        "dm": frb_dict["dm"],
        "sn": frb_dict["sn"],
        "width": frb_dict["width"],
        # "search_path": frb_dict["search_path"],
        # "image_path" : frb_dict["image_path"],
        # "histogram_path": frb_dict["histogram_path"],
    }
    with open(frb_dict["search_path"], 'rb') as search, open(frb_dict["image_path"], 'rb') as image, open(frb_dict["histogram_path"], 'rb') as histogram:
        r = session.post(
            url,
            data=data,
            files={
                "search_open":search,
                "image_open":image,
                "histogram_open":histogram,
            }
        )
    print(r)


if __name__ == '__main__':
    loglevels = dict(DEBUG=logging.DEBUG,
                     INFO=logging.INFO,
                     WARNING=logging.WARNING)
    parser = argparse.ArgumentParser(description='Upload a FRB candidate to the database.')
    parser.add_argument('--yaml', type=str,
                        help='Path to the yaml file containing FRB information.')
    parser.add_argument("-L", "--loglvl", type=str, help="Logger verbosity level. Default: INFO",
                                    choices=loglevels.keys(), default="INFO")
    args = parser.parse_args()

    # set up the logger for stand-alone execution
    formatter = logging.Formatter('%(asctime)s  %(name)s  %(lineno)-4d  %(levelname)-9s :: %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    # Set up local logger
    logger.setLevel(args.loglvl)
    logger.addHandler(ch)
    logger.propagate = False

    frbevent_upload(args.yaml)