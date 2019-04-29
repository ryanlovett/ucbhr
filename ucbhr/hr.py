# vim:set et sw=4 ts=4:
import logging
import sys

from tornado import escape
from tornado import httpclient
from tornado.httputil import url_concat

# logging
logging.basicConfig(stream=sys.stdout, level=logging.NOTSET)
logger = logging.getLogger(__name__)

# Various SIS endpoints
employees_url = "https://apis.berkeley.edu/hr/v3/employees"

async def get_hr_items(url, params, headers, item_type):
    '''Get a list of items (enrollments, ) from the SIS.'''
    http_client = httpclient.AsyncHTTPClient()
    response = await http_client.fetch(url_concat(url, params), headers=headers)
    data = escape.json_decode(response.body)

    # return if there is no response in the data (e.g. 404)
    if 'response' not in data or len(data['response']) == 0:
        logger.warn('No response in data')
        return[]
    # return if the item_type has no items
    elif item_type not in data['response'][0]:
        logger.warn(f'No {item_type}')
        return []
    return data['response'][0][item_type]

async def get_jobs(app_id, app_key, identifier, id_type):
    '''Given a campus-uid return the jobs.'''
    url = f"{employees_url}/{identifier}/jobs"
    headers = {
        "Accept": "application/json",
        "app_id": app_id,
        "app_key": app_key
    }
    params = { "id-type": id_type }
    logger.debug(f"get_jobs: {url} {params}")
    jobs = await get_hr_items(url, params, headers, 'jobs')
    logger.debug(f'jobs: {jobs}')
    return jobs

def job_code(job):
    return job['position']['jobCode']['code']['code']

def job_description(job):
    return job['position']['jobCode']['code']['description']

def job_department_code(job):
    return job['department']['code']

def job_department_description(job):
    return job['department']['description']
