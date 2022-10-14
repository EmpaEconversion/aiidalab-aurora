# -*- coding: utf-8 -*-

import aiida
from aiida import load_profile
load_profile()
from aiida.orm import load_node, load_code, load_computer, load_group
from aiida.engine import submit
from aiida.common.exceptions import NotExistent
from time import sleep

BatterySampleData = aiida.plugins.DataFactory('aurora.batterysample')
CyclingSpecsData = aiida.plugins.DataFactory('aurora.cyclingspecs')
TomatoSettingsData = aiida.plugins.DataFactory('aurora.tomatosettings')
BatteryCyclerExperiment = aiida.plugins.CalculationFactory('aurora.cycler')

TomatoMonitorData = aiida.plugins.DataFactory('calcmonitor.monitor.tomatobiologic')
TomatoMonitorCalcjob = aiida.plugins.CalculationFactory('calcmonitor.calcjob_monitor')

# MONITOR_CODE = load_code("monitor@localhost-verdi")
GROUP_SAMPLES = load_group("BatterySamples")
GROUP_METHODS = load_group("CyclingSpecs")
GROUP_CALCJOBS = load_group("CalcJobs")
GROUP_MONITORS = load_group("MonitorJobs")

def _find_job_remote_folder(job):
    MAX_TIME = 60
    remote_folder = False
    for t in range(MAX_TIME):
        # perform query job.outputs.remote_folder
        try:
            remote_folder = job.get_outgoing().get_node_by_label('remote_folder')
        except NotExistent:
            pass
        else:
            print("Remote folder found. Setting up monitor job...")
            return remote_folder
        sleep(2)
    else:  # the MAX_TIME was reached
        raise RuntimeError(f"Remote folder of job {job.pk} not found. Is the daemon running?")

    return remote_folder

def submit_experiment(sample, method, tomato_settings, monitor_job_settings, code_name,
    sample_node_label="", method_node_label="", calcjob_node_label=""):
    """
    sample : `aurora.schemas.battery.BatterySample`
    method : `aurora.schemas.cycling.ElectroChemSequence`
    tomato_settings : `aurora.schemas.dgbowl_schemas.Tomato_0p2`
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
    
    job = submit(builder)
    job.label = calcjob_node_label
    print(f"Job <{job.pk}> submitted to AiiDA...")
    GROUP_CALCJOBS.add_nodes(job)

    if monitor_job_settings:

        monitor_protocol = TomatoMonitorData(dict={
            'sources': {
                'output': {
                    'filepath': 'snapshot.json',
                    'refresh_rate': monitor_job_settings['refresh_rate']
                },
            },
            'options': {
                'check_type': monitor_job_settings['check_type'],
                'consecutive_cycles': monitor_job_settings['consecutive_cycles'],
                'threshold': monitor_job_settings['threshold'],
            },
            'retrieve': ['results.json'],
            'retrieve_temporary': ['results.zip']
        })
        monitor_protocol.store()
        monitor_protocol.label = "" # TODO? write default name generator - e.g "monitor-rate_600-cycles_2-thr_0.80"

        monitor_builder = TomatoMonitorCalcjob.get_builder()
        monitor_builder.code = MONITOR_CODE
        monitor_builder.metadata.options.parser_name = "calcmonitor.cycler"
        monitor_builder.monitor_protocols = {'monitor1': monitor_protocol}

        monitor_builder.monitor_folder = _find_job_remote_folder(job)

        mjob = submit(monitor_builder)
        if job.label:
            mjob.label = f"{job.label}-monitor"
        print(f"Monitor Job <{mjob.pk}> submitted to AiiDA...")
        GROUP_MONITORS.add_nodes(mjob)

    return job
