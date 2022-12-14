.. _upload-cand:

Uploading FRB Events
====================

Running the Upload Script
-------------------------

To upload your FRB events and follow up measurements you can use `this <https://github.com/ADACS-Australia/FRB_candidates_app/blob/main/frb_cand/upload_cand.py>`_ python script.
To use it you must set the environment variables `FRB_USER` and `FRB_PASS` which is your username and password for the `FRB web app <https://frb-classifier.duckdns.org/>`_ account.

For the first detection/measurement of the FRB event, you can upload the radio measurement and observation data with a command like the following:

.. code-block::

    python upload_cand.py --first --radio_yaml radio_example.yaml --observation_yaml observation_example.yaml


Which will output an ID like so:

.. code-block::

    3

This should be recorded and used for future measurement updates (through post-processing and optical follow up).

To upload further measurements, use the update option like so:

.. code-block::

    python upload_cand.py --update 3 --radio_yaml radio_example.yaml

Note that you don't need the observation YAML after the first detection.

Radio Measurement YAML Format
-----------------------------

Here is an example of what the radio measurement YAML can look like

.. code-block::

    {
        # Only used for first detection/measurement
        "time_of_arrival": "2017-11-17T12:21:38.87",
        "repeater": true,
        "search_path": "example_search.png",
        "image_path" : "example_image.png",
        "histogram_path": "example_histogram.png",

        # Required
        "dm": 411.0,
        "dm_err": 1.0,
        "ra": 77.01461542,
        "ra_err": 0.05,
        "dec": 26.06069556,
        "dec_err": 0.05,
        "sn": 50,
        "width": 5,
        "flux": 35,
        "flux_err": 3,
        "source": "MB",
        "version": "v1.0",

        # Optional
        "fluence": 45,
        "fluence_err": 5,
        "dmism": 123.16007817568256,
        "rm": -613.0,
        "rm_err": 2.0,
        "cosmo": "Planck18",
        "eellipse": {
            "a": 0.004,
            "b": 0.004,
            "cl": 68.0,
            "theta": 0.0
        },
        "z": 0.0982,
    }



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

"dm" : `float`
    The dispersion measure of the FRB in pc / cm^3

"dm_err" : `float`
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

"flux": `float`, optional
    The flux density of the event in Jy

"flux_err": `float`, optional
    The error of the flux density of the event in Jy

"source": `str`
    The source (telescope pipeline) of the measurements, should be either MB (Multi-Beam) or HT (High-Time resolution)

"version": `str`
    The version of the "source" software

"fluence": `float`, optional
    The fluence of the event in Jy ms

"fluence_err": `float`, optional
    The error of the fluence of the event in Jy ms

"dmism" : `float`, optional
    The estimated amount of the dispersion measure that is contributed by the interstellar medium in pc / cm^3

"rm": `float`, optional
    The Rotation Measure of the candidate in rad / m^2

"rm_err": `float`, optional
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
            The angle in degrees from North clockwise

"z": `boolean`, optional
    The redshift of the candidate


Observation YAML Format
-----------------------

Here is an example of what the observation YAML can look like

.. code-block::

    {
        "beam_semi_major_axis": 0.2,
        "beam_semi_minor_axis": 0.3,
        "beam_rotation_angle": 45,
        "sampling_time": 0.1,
        "bandwidth": 300,
        "nchan": 3000,
        "centre_frequency": 1400,
        "npol": 2,
        "bits_per_sample": 8,
        "gain": 3,
        "tsys": 50,
        "backend": "Multibeam",
        "beam": 1,
    }


"beam_semi_major_axis": `float`
    The beam semi major axis in arcminutes.

"beam_semi_minor_axis": `float`
    The beam semi minor axis in arcminutes.

"beam_rotation_angle": `int`
    The beam rotation angle in degrees, clockwise from North.

"sampling_time": `float`
    The duration of each sample in ms.

"bandwidth": `float`
    The bandwidth in MHz.

"nchan": `int`
    The number of frequency channels.

"centre_frequency": float`
    The centre frequency in MHz.

"npol": `int`
    The number of antena polarisations.

"bits_per_sample": `int`
    The size in bits of each sample.

"gain": `float`
    The gain of telescope in K/Jy.

"tsys": `float`
    The system temperature in K.

"backend": `string`
    The name of the telescope backend being used ("Multibeam" for example).

"beam": `int`
    The beam number for multi beam receivers.