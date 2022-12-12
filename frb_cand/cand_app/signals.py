import logging
import subprocess

import voeventparse as vp
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from .models import FRBEvent, RadioMeasurement, VOEvent
from .views import slack_event_post, submit_frb_to_tns

logger = logging.getLogger(__name__)

@receiver(post_save, sender=FRBEvent)
def slack_trigger(sender, instance, **kwargs):
    """Each time an event is created, send a slack notification.
    """
    print(f"posting {instance.id}")
    slack_event_post(instance.id)

@receiver(post_save, sender=RadioMeasurement)
def tns_trigger(sender, instance, **kwargs):
    """Each time the first position is uploaded, send it to the Tranisent Name Server.
    """
    logger.debug(f"Checking {instance.frb}")
    frb_mes = RadioMeasurement.objects.filter(frb=instance.frb)
    if len(frb_mes) == 1:
        # This is the first postion so upload it
        tns_name = submit_frb_to_tns(instance.frb.id)
        print(f"tns_name: {tns_name}")
        # Grab FRB event and update TNS name
        # do it this way to prevent a save triggering another slack trigger
        FRBEvent.objects.filter(id=instance.frb.id).update(tns_name=tns_name)

        # Create voevent (waiting for TNS may make this too slow)
        make_voevent(instance)


def make_voevent(radio_measurement):
    # Grab observation information
    obs = radio_measurement.frb.observation
    # initialise event
    v = vp.Voevent(
        stream='frb-classifier.duckdns.org/CRAFT',
        stream_id=radio_measurement.id,
        role=vp.definitions.roles.test, #TODO turn off test
    )

    # Who
    vp.set_who(
        v,
        date=radio_measurement.datetime,
        author_ivorn='frb-classifier.duckdns.org/CRAFT'
    )
    vp.set_author(
        v,
        title='CRAFT_bot',
        shortName='CRAFT',
        contactName='Ryan Shannon',
        contactEmail='rshannon@swin.edu.au',
        contactPhone='+61 0392145205',
    )

    # What

    # observatory paramaters group
    beam_semi_major_axis = vp.Param(
        name='beam_semi-major_axis',
        value=str(obs.beam_semi_major_axis),
        unit='MM',
        ucd='instr.beam;pos.errorEllipse;phys.angSize.smajAxis',
        dataType='float',
    )
    beam_semi_minor_axis = vp.Param(
        name='beam_semi-minor_axis',
        value=str(obs.beam_semi_minor_axis),
        unit='MM',
        ucd='instr.beam;pos.errorEllipse;phys.angSize.sminAxis',
        dataType='float',
    )
    beam_rotation_angle = vp.Param(
        name='beam_rotation_angle',
        value=str(obs.beam_rotation_angle),
        unit='Degrees',
        ucd='instr.beam;pos.errorEllipse;instr.offset',
        dataType='float',
    )
    sampling_time = vp.Param(
        name='sampling_time',
        value=str(obs.sampling_time),
        unit='ms',
        ucd='time.resolution',
        dataType='float',
    )
    bandwidth = vp.Param(
        name='bandwidth',
        value=str(obs.bandwidth),
        unit='MHz',
        ucd='instr.bandwidth',
        dataType='float',
    )
    nchan = vp.Param(
        name='nchan',
        value=str(obs.nchan),
        unit='None',
        ucd='meta.number;em.freq;em.bin',
        dataType='int',
    )
    centre_frequency = vp.Param(
        name='centre_frequency',
        value=str(obs.centre_frequency),
        unit='MHz',
        ucd='em.freq;instr',
        dataType='float',
    )
    npol = vp.Param(
        name='npol',
        value=str(obs.npol),
        unit='None',
        dataType='int',
    )
    bits_per_sample = vp.Param(
        name='bits_per_sample',
        value=str(obs.bits_per_sample),
        unit='None',
        dataType='int',
    )
    gain = vp.Param(
        name='gain',
        value=str(obs.gain),
        unit='K/Jy',
        dataType='float',
    )
    tsys = vp.Param(
        name='tsys',
        value=str(obs.tsys),
        unit='K',
        ucd='phot.antennaTemp',
        dataType='float',
    )
    backend = vp.Param(
        name='backend',
        value=str(obs.backend),
        dataType='string',
    )
    beam = vp.Param(
        name='beam',
        value=str(obs.beam),
        dataType='int',
    )
    beam.Description = 'Detection beam number if backend is a multi beam receiver'
    v.What.append(
        vp.Group(
            params=[
                beam_semi_major_axis,
                beam_semi_minor_axis,
                beam_rotation_angle,
                sampling_time,
                bandwidth,
                nchan,
                centre_frequency,
                npol,
                bits_per_sample,
                gain,
                tsys,
                backend,
                beam,
            ],
            name='observatory parameters'
        )
    )

    # Event paramater group
    dm = vp.Param(
        name='dm',
        value=str(radio_measurement.dm),
        unit='pc/cm^3',
        ucd='phys.dispMeasure',
        dataType='float',
    )
    dm_error = vp.Param(
        name='dm_error',
        value=str(radio_measurement.dm_err),
        unit='pc/cm^3',
        ucd='stat.error;phys.dispMeasure',
        dataType='float',
    )
    width = vp.Param(
        name='width',
        value=str(radio_measurement.width),
        unit='ms',
        ucd='time.duration;src.var.pulse',
        dataType='float',
    )
    snr = vp.Param(
        name='snr',
        value=str(radio_measurement.sn),
        ucd='stat.snr',
        dataType='float',
    )
    flux = vp.Param(
        name='flux',
        value=str(radio_measurement.flux),
        unit='Jy',
        ucd='phot.flux',
        dataType='float',
    )
    gl = vp.Param(
        name='gl',
        value=str(radio_measurement.gl),
        unit='Degrees',
        ucd='pos.galactic.lon',
        dataType='float',
    )
    gb = vp.Param(
        name='gb',
        value=str(radio_measurement.gb),
        unit='Degrees',
        ucd='pos.galactic.lat',
        dataType='float',
    )
    v.What.append(
        vp.Group(
            params=[
                dm,
                dm_error,
                width,
                snr,
                flux,
                gl,
                gb,
            ],
            name='event parameters'
        )
    )

    # Where and when
    vp.add_where_when(
        v,
        coords=vp.Position2D(
            ra=radio_measurement.ra,
            dec=radio_measurement.dec,
            # Use average ra and dec error
            err=(radio_measurement.ra_pos_error + radio_measurement.dec_pos_error) / 2,
            units='deg',
            system=vp.definitions.sky_coord_system.utc_fk5_geo,
        ),
        obs_time=radio_measurement.frb.time_of_arrival,
        observatory_location=vp.definitions.observatory_location.geosurface
    )

    # How
    vp.add_how(
        v,
        descriptions='Discovered using the CRACO pipeline',
        references=vp.Reference('https://frb-classifier.duckdns.org/'),
    )

    # Why
    # TODO check if there is a probability statistic that we can add as why
    # vp.add_why(
    #     v,
    #     importance=0.5,
    #     inferences=vp.Inference(
    #         probability=0.1,
    #         relation='identified',
    #         name='GRB121212A',
    #         concept='process.variation.burst;em.radio'
    #     )
    # )

    # Check everything is schema compliant:
    vp.assert_valid_as_v2_0(v)

    # Prettyprint as a check:
    print(vp.prettystr(v))

    # Echo the xml file
    output_bash_dump = vp.dumps(v).decode()
    echo_pipe  = subprocess.Popen(['echo', output_bash_dump], stdout=subprocess.PIPE)
    # Pipe that echo to the standard out of comet-sendvo
    comet_process = subprocess.Popen(['comet-sendvo', '--host=localhost'], stdout=subprocess.PIPE, stdin=echo_pipe.stdout)
    stdout = comet_process.communicate()[0].decode()

    # Print as a debug check
    for i in stdout.split("\n"):
        print(i)

    # Save the xml and log to the database
    new_event = VOEvent(
        radio_measurement=radio_measurement,
        xml_packet=vp.dumps(v),
        comet_log=stdout,
    )
    new_event.save()
