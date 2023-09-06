import logging
import sys

import jmespath

from . import hr

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

async def get(app_id, app_key, identifier, id_type):
    '''Given a campus-uid return the jobs.'''
    url = f"{hr.employees_url}/{identifier}/jobs"
    headers = {
        "Accept": "application/json",
        "app_id": app_id,
        "app_key": app_key
    }
    params = { "id-type": id_type }
    logger.debug(f"get_jobs: {url} {params}")
    jobs = await hr.get_hr_items(url, params, headers, "jobs")
    logger.debug(f'jobs: {jobs}')
    return jobs

def code(job):
    return jmespath.search("position.jobCode.code.code", job)

def description(job):
    return jmespath.search("position.jobCode.code.description", job)

def department_code(job):
    return jmespath.search("department.code", job)

def department_description(job):
    return jmespath.search("department.description", job)

def status(job):
    return jmespath.search("position.jobCode.status.description", job)
