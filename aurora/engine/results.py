import datetime
import aiida
from aiida import load_profile
from aiida.orm import Group, QueryBuilder, load_node
import aiida_aurora.utils

load_profile()
BatteryCyclerExperiment = aiida.plugins.CalculationFactory('aurora.cycler')

def query_jobs(last_days=0, group='CalcJobs'):
    qb = QueryBuilder()
    qb.append(Group, filters={'label': group}, tag='g')
    qb.append(BatteryCyclerExperiment, with_group='g', tag='jobs',
             project=['id', 'label', 'ctime', 'attributes.process_label', 'attributes.state', 'attributes.status', 'extras.monitored'])
    if last_days:
        qb.add_filter('jobs', {'ctime': {'>=': datetime.datetime.now() - datetime.timedelta(days=last_days)}})
    qb.order_by({'jobs': {'ctime': 'desc'}})
    return [q['jobs'] for q in qb.dict()]

def cycling_analysis(job_id):
    job_node = load_node(pk=job_id)
    data = aiida_aurora.utils.cycling_analysis.cycling_analysis(job_node)
    return data