Software Developer Documentation
================================

Uploading data
--------------
Users will upload data to the database with the :ref:`upload_cand.py <upload-cand>` script, which parses input YAML files and puts the data into the relevant tables.
The triggered steps are handled using ``signals.py``, which will be explained in the next sections.


Slack Integration
------------------
Each time a new ``FRBEvent`` is created, the ``slack_trigger`` and ``slack_event_post`` functions in ``signals.py``
will be triggered and send off a Slack message describing the event.
This is done in the ``slack_event_post`` view, which makes a block for each image and two response buttons.

The Slack App that handles this is `frb_cand <https://craft-askap.slack.com/apps/A046XKC9J2X-frb-cand?tab=settings&next_id=0>`_
which posts to the private channel ``nick_frb_cand_testing`` currently.
This is sent to slack using a webhook URL, which should be set in the settings.ini and changed
`here <https://api.slack.com/apps/A046XKC9J2X/incoming-webhooks>`_ (if you have permissions).


This could be changed in production, or making a separate app for production may be more manageable.
The required permissions are

* Post messages to specific channels in Slack

* View basic information about public channels in a workspace

* Send messages as @frbcand (or whatever the new app name is)

* Post messages to a private group

The buttons will return a JSON dump to the web app through the ``slack_get_rating`` view.
The URL for the app is set within the `Interactivity & Shortcuts <https://api.slack.com/apps/A046XKC9J2X/interactive-messages?>`_
settings page for the app (currently https://frb-classifier.duckdns.org/slack_get_rating/).
The JSON is parsed, and the rating is recorded in the database and with a slack message.


Transient Name Server Integration
----------------------------------
The TNS has a production version (https://www.wis-tns.org/) and a testing version (https://sandbox.wis-tns.org/) of the site.
We currently only use the testing sandbox version. There is some `documentation <https://www.wis-tns.org/content/tns-getting-started>`_ but it is lacking for the FRB API.

We only submit the first FRB radio measurement to the TNS.
It submits the FRBEvent with the ``submit_frb_to_tns`` view, which dumps a JSON the TNS CRAFT_bot and then waits for a response that contains the transient name.
We then record this name in the database.

You should have access to the CRAFT_bot as long as you have access to the CRAFT TNS group.
You can request an invite to the CRAFT TNS group from Ryan Shannon.

Sometimes the API stops working, but updating the API key fixes it.
Go to the `Edit CRAFT_bot page <https://sandbox.wis-tns.org/node/143623/edit?destination=bots>`_
and tick "Create new API Key" and click save.
Copy the key it outputs into the ``TNS_API_KEY`` in the ``settings.ini`` and restart the server.


VOEvent Integration
--------------------
Currently, we only locally (not to a broker) submit VOEvents for the first radio detection (no follow-ups or event withdrawals).
``make_voevent`` in ``signals.py`` creates the VOEvent using `voevent-parse <https://voevent-parse.readthedocs.io/en/stable/index.html>`_
and using `this <https://github.com/ebpetroff/FRB_VOEvent/blob/master/templates/01-Detection.xml>`_ template.
It then submits the event using ``comet-sendvo`` and records it in the database.
