# from time import sleep

import aiida
from aiida.engine import submit
from aiida.manage.configuration import load_profile
from aiida.orm import Dict, load_code, load_group

load_profile()

BatterySampleData = aiida.plugins.DataFactory('aurora.batterysample')
CyclingSpecsData = aiida.plugins.DataFactory('aurora.cyclingspecs')
TomatoSettingsData = aiida.plugins.DataFactory('aurora.tomatosettings')
BatteryCyclerExperiment = aiida.plugins.CalculationFactory('aurora.cycler')

GROUP_SAMPLES = load_group("BatterySamples")
GROUP_METHODS = load_group("CyclingSpecs")
GROUP_CALCJOBS = load_group("CalcJobs")


def submit_experiment(sample,
                      method,
                      tomato_settings,
                      monitor_settings,
                      code_name,
                      sample_node_label="",
                      method_node_label="",
                      calcjob_node_label=""):
    """
    sample : `aiida_aurora.schemas.battery.BatterySample`
    method : `aiida_aurora.schemas.cycling.ElectroChemSequence`
    tomato_settings : `aiida_aurora.schemas.dgbowl_schemas.Tomato_0p2`
    """

    sample_node = BatterySampleData(sample.dict())
    if sample_node_label:
        sample_node.label = sample_node_label
    sample_node.store()
    GROUP_SAMPLES.add_nodes(sample_node)

    method_node = CyclingSpecsData(method.dict())
    if method_node_label:
        method_node.label = method_node_label
    method_node.store()
    GROUP_METHODS.add_nodes(method_node)

    tomato_settings_node = TomatoSettingsData(tomato_settings.dict())
    tomato_settings_node.label = ""  # TODO? write default name generator - e.g. "tomato-True-monitor_600"
    tomato_settings_node.store()

    code = load_code(code_name)

    builder = BatteryCyclerExperiment.get_builder()
    builder.battery_sample = sample_node
    builder.code = code
    builder.technique = method_node
    builder.control_settings = tomato_settings_node

    if monitor_settings:
        refresh_rate = monitor_settings.pop("refresh_rate", 600)
        builder.monitors = {
            "capacity":
            Dict({
                "entry_point": "aurora.monitors.capacity_threshold",
                "minimum_poll_interval": refresh_rate,
                "kwargs": {
                    "settings": monitor_settings,
                    "filename": "snapshot.json",
                },
            }),
        }

    job = submit(builder)
    job.label = calcjob_node_label
    print(f"Job <{job.pk}> submitted to AiiDA...")
    GROUP_CALCJOBS.add_nodes(job)

    if monitor_settings:
        job.set_extra('monitored', True)
    else:
        job.set_extra('monitored', False)

    return job
