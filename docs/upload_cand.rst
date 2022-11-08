Uploading FRB Events
====================

Running the Upload Script
-------------------------

To upload your FRB events and follow up measurements you can use `this <https://github.com/ADACS-Australia/FRB_candidates_app/blob/main/frb_cand/upload_cand.py>`_ python script.
To use it you must set the environment variables `FRB_USER` and `FRB_PASS` which is your username and password for the `FRB web app <https://frb-classifier.duckdns.org/>`_ account.

For the first detection/measurement of the FRB event, you can use a command like the following:

.. code-block::

    python upload_cand.py --first --radio_yaml example.yaml


Which will output an ID like so:

.. code-block::

    3

This should be recorded and used for future measurement updates (through post-processing and optical follow up).

To upload further measurements, use the update option like so:

.. code-block::

    python upload_cand.py --update 3 --radio_yaml example.yaml

Radio Measurement YAML Format
-----------------------------

Here is an example of what the YAML can look like

.. code-block::

    {
        # Only used for first detection/measurement
        "time_of_arrival": "2017-11-17T12:21:38.87"
        "repeater": true,
        "search_path": "example_search.png",
        "image_path" : "example_image.png",
        "histogram_path": "example_histogram.png",

        # Required
        "DM": 411.0,
        "DM_err": 1.0,
        "ra": 77.01461542,
        "ra_err": 0.05,
        "dec": 26.06069556,
        "dec_err": 0.05,
        "sn": 50,
        "width": 5,
        "source": "MB",
        "version": "v1.0",

        # Optional
        "fluence": 45
        "fluence_err": 5
        "DMISM": 123.16007817568256,
        "RM": -613.0,
        "RM_err": 2.0,
        "cosmo": "Planck18",
        "eellipse": {
            "a": 0.004,
            "b": 0.004,
            "cl": 68.0,
            "theta": 0.0
        },
        "z": 0.0982,
    }


#TODO NOTES: ra and dec error are redundant if eellipse is always used, what is cosmo used for? Where is theta measured from?

Each of the keys:

"time_of_arrival": `str`, optional
    The time of arrival of the FRB in the format "%Y-%m-%dT%H:%M:%S.%f", eg. "2017-11-17T12:21:38.87"

"repeater": `boolean`, optional
    Is the FRB a repeater (true or false)?

"search_path": `str`, optional
    The path to the search image

"image_path" :  `str`, optional
    The path to the radio image

"histogram_path": `str`, optional
    The path to the histogram image

"DM" : `float`
    The dispersion measure of the FRB in pc / cm^3

"DM_err" : `float`
    The error of the dispersion measure of the FRB in pc / cm^3

"ra": `str`
    The Right Acension of the candidate in degrees

"ra_err": `str`
    The error of the Right Acension of the candidate in degrees

"dec": `str`
    The Declination of the candidate in degrees

"dec_err": `str`
    The error of the Declination of the candidate in degrees

"sn": `float`
    The signal-to-noise ration of the candidate

"width": `float`
    The width of the candidate pulse in ms

"source": `str`
    The source (telescope pipeline) of the measurements, should be either MB (Multi-Beam) or HT (High-Time resolution)

"version": `str`
    The version of the "source" software

"fluence": `float`, optional
    The fluence of the event in Jy ms

"fluence_err": `float`, optional
    The error of the fluence of the event in Jy ms

"DMISM" : `float`, optional
    The estimated amount of the dispersion measure that is contributed by the interstellar medium in pc / cm^3

"RM": `float`, optional
    The Rotation Measure of the candidate in rad / m^2

"RM_err": `float`, optional
    The error of the Rotation Measure of the candidate in rad / m^2

"cosmo": `str`, optional
    The cosmological model used for cosmological calculations, eg. "Planck18"

"eellipse": `object`, optional
    The error ellipse object which has the following keys within it

        "a": `float`
            The width of the ellipse in degrees
        "b": `float`
            The height of the ellipse in degrees
        "cl": `float`, optional
            The confidence level of the error ellipse in percent. Default 68.0
        "theta": `float`
            The angle in degrees

"z": `boolean`, optional
    The redshift of the candidate