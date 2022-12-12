#!/usr/bin/env python

import argparse
import json
import logging
import os
import sys

import astropy.units as u
import requests
import yaml
from astropy.coordinates import SkyCoord

logger = logging.getLogger(__name__)

SYSTEM_ENV = os.environ.get('SYSTEM_ENV', None)
if SYSTEM_ENV == 'DEVELOPMENT':
    BASE_URL = 'http://127.0.0.1:8000'
else:
    BASE_URL = 'https://frb-classifier.duckdns.org'


class TokenAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = "Token {}".format(self.token)
        return r


def observation_upload(yaml_path):
    """Upload an observation for a FRB event to the database.

    Parameters
    ----------
    yaml_path : `str`
        The full path of the yaml file containing FRB data.
    """
    # Set up connection
    session = requests.session()
    session.auth = session.auth = (os.environ['FRB_USER'], os.environ['FRB_PASS'])
    url = f'{BASE_URL}/observation_create/'

    # Load yaml file
    with open(yaml_path, 'r') as file:
        frb_dict = yaml.safe_load(file)

    # Required data
    data = {
        "beam_semi_major_axis": frb_dict["beam_semi_major_axis"],
        "beam_semi_minor_axis": frb_dict["beam_semi_minor_axis"],
        "beam_rotation_angle": frb_dict["beam_rotation_angle"],
        "sampling_time": frb_dict["sampling_time"],
        "bandwidth": frb_dict["bandwidth"],
        "nchan": frb_dict["nchan"],
        "centre_frequency": frb_dict["centre_frequency"],
        "npol": frb_dict["npol"],
        "bits_per_sample": frb_dict["bits_per_sample"],
        "gain": frb_dict["gain"],
        "tsys": frb_dict["tsys"],
        "backend": frb_dict["backend"],
        "beam": frb_dict["beam"],
    }

    r = session.post(
        url,
        data=data,
    )
    # Return the observation id that was just created
    return json.loads(r.text)["id"]


def frbevent_upload(observation_id, yaml_path):
    """Upload an FRB event to the database.

    Parameters
    ----------
    observation_id : `int`
        The ID of the observation ID to link this FRB event to.
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
        "observation": observation_id,
        "time_of_arrival": frb_dict["time_of_arrival"],
        "repeater": frb_dict["repeater"],
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


def radio_measurement_upload(id, yaml_path):
    """Upload an radio_measurement for a FRB event to the database.

    Parameters
    ----------
    id : `int`
        The ID of the FRB event to link this radio_measurement to.
    yaml_path : `str`
        The full path of the yaml file containing FRB data.
    """
    # Set up connection
    session = requests.session()
    session.auth = session.auth = (os.environ['FRB_USER'], os.environ['FRB_PASS'])
    url = f'{BASE_URL}/radio_measurement_create/'

    # Load yaml file
    with open(yaml_path, 'r') as file:
        frb_dict = yaml.safe_load(file)

    # Create skycoord object for future conversions
    coord = SkyCoord(frb_dict["ra"], frb_dict["dec"], unit=(u.deg, u.deg))

    # Required data
    data = {
        "frb": id,
        "ra": frb_dict["ra"],
        "dec": frb_dict["dec"],
        # Convert from deg to hms or dms
        "ra_hms":  coord.ra.to_string(unit=u.hour),
        "dec_dms": coord.dec.to_string(unit=u.deg),
        "ra_pos_error":  frb_dict["ra_err"],
        "dec_pos_error": frb_dict["dec_err"],
        "source": frb_dict["source"],
        "version": frb_dict["version"],
        "dm": frb_dict["dm"],
        "dm_err": frb_dict["dm_err"],
        "sn": frb_dict["sn"],
        "width": frb_dict["width"],
        "flux": frb_dict["flux"],
        "flux_err": frb_dict["flux_err"],
        # Convert to Galactic coordinates
        "gl":  coord.galactic.l.deg,
        "gb": coord.galactic.b.deg,
    }
    # Check for optional data
    if "z" in frb_dict.keys():
        data["z"] = frb_dict["z"]
    if "rm" in frb_dict.keys() and "rm_err" in frb_dict.keys():
        data["rm"] = frb_dict["rm"]
        data["rm_err"] = frb_dict["rm_err"]
    if "fluence" in frb_dict.keys() and "fluence_err" in frb_dict.keys():
        data["fluence"] = frb_dict["fluence"]
        data["fluence_err"] = frb_dict["fluence_err"]

    r = session.post(
        url,
        data=data,
    )
    # Return the event id that was just created
    return r


if __name__ == '__main__':
    loglevels = dict(
        DEBUG=logging.DEBUG,
        INFO=logging.INFO,
        WARNING=logging.WARNING
    )
    parser = argparse.ArgumentParser(description='Upload a FRB candidate to the database.')
    parser.add_argument('-f', '--first', action='store_true',
                        help='If this is the first detection of the FRB (will make a new FRB Event instead of using a previous ID).')
    parser.add_argument('-u', '--update', type=int,
                        help='The ID of the FRB to update with the latest measurements.')
    parser.add_argument('-o', '--observation_yaml', type=str,
                        help='Path to the yaml file containing FRB information.')
    parser.add_argument('-r', '--radio_yaml', type=str,
                        help='Path to the yaml file containing FRB information.')
    parser.add_argument('--optical_yaml', type=str,
                        help='Path to the yaml file containing FRB information.')
    parser.add_argument("-L", "--loglvl", type=str, choices=loglevels.keys(), default="INFO",
                        help="Logger verbosity level. Default: INFO",)
    args = parser.parse_args()

    # set up the logger for stand-alone execution
    formatter = logging.Formatter('%(asctime)s  %(name)s  %(lineno)-4d  %(levelname)-9s :: %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    # Set up local logger
    logger.setLevel(args.loglvl)
    logger.addHandler(ch)
    logger.propagate = False

    if args.first:
        if not args.radio_yaml:
            logger.error("No radio YAML included. Please use --radio_yaml to include it. Exiting.")
            sys.exit(1)
        if not args.observation_yaml:
            logger.error("No observation YAML included. Please use --observation_yaml to include it. Exiting.")
            sys.exit(1)
        observation_id = observation_upload(args.observation_yaml)
        frb_event_id = frbevent_upload(observation_id, args.radio_yaml)
        print(frb_event_id)
        radio_measurement_upload(frb_event_id, args.radio_yaml)
    elif args.update:
        if args.radio_yaml:
            radio_measurement_upload(args.update, args.radio_yaml)
    else:
        logger.error("Please use either --first or --update. Exiting.")
        sys.exit(1)