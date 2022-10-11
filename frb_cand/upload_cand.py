#!/usr/bin/env python

import os
import argparse
import requests
import json
import yaml

from astropy.coordinates import SkyCoord
import astropy.units as u

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
    """Upload an FRB event to the database.

    Parameters
    ----------
    yaml_path : `str`
        The full path of the yaml file containing FRB data.
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
    # Return the event id that was just created
    return json.loads(r.text)["id"]


def position_upload(id, yaml_path, source="MB"):
    """Upload an position for a FRB event to the database.

    Parameters
    ----------
    id : `int`
        The ID of the FRB event to link this position to.
    yaml_path : `str`
        The full path of the yaml file containing FRB data.
    """
    # Set up connection
    session = requests.session()
    session.auth = session.auth = (os.environ['FRB_USER'], os.environ['FRB_PASS'])
    url = f'{BASE_URL}/position_create/'

    # Load yaml file
    with open(yaml_path, 'r') as file:
        frb_dict = yaml.safe_load(file)

    # convert coord to degrees
    coord = SkyCoord(frb_dict["ra_hms"], frb_dict["dec_hms"], unit=(u.hour, u.deg))

    data = {
        "frb": id,
        "ra": coord.ra.deg,
        "dec": coord.dec.deg,
        "ra_hms":  frb_dict["ra_hms"],
        "dec_dms": frb_dict["dec_hms"],
        "ra_pos_error":  frb_dict["ra_unc"],
        "dec_pos_error": frb_dict["dec_unc"],
        "source": source,
    }
    r = session.post(
        url,
        data=data,
    )
    # Return the event id that was just created
    print(r.status)
    return r


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

    frb_event_id =  frbevent_upload(args.yaml)
    position_upload(frb_event_id, args.yaml, source="MB")