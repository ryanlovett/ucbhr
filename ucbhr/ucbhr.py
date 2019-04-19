# vim:set et sw=4 ts=4:
import logging
import sys

from tornado import escape
from tornado import httpclient
from tornado.httputil import url_concat

# logging
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logger = logging.getLogger(__name__)

# Various SIS endpoints
employees_uri = "https://apis.berkeley.edu/hr/v3/employees"

async def get_hr_items(uri, params, headers, item_type):
    '''Get a list of items (enrollments, ) from the SIS.'''
    logger.info(f"getting {item_type}")
    http_client = httpclient.AsyncHTTPClient()
    response = await http_client.fetch(url_concat(uri, params), headers=headers)
    data = escape.json_decode(response.body)

    # return if there is no response in the data (e.g. 404)
    if 'response' not in data or len(data['response']) == 0:
        logger.debug('No response in data')
        return[]
    # return if the item_type has no items
    elif item_type not in data['response'][0]:
        logger.debug(f'No {item_type}')
        return []
    return data['response'][0][item_type]

async def get_jobs(app_id, app_key, identifier, id_type):
    '''Given a campus-uid return the jobs.'''
    headers = {
        "Accept": "application/json",
        "app_id": app_id,
        "app_key": app_key
    }
    params = { "id-type": id_type }

    uri = employees_uri + f"/{identifier}/jobs"
    logger.debug(f"get_jobs: {uri} {params}")
    jobs = await get_hr_items(uri, params, headers, 'jobs')
    return jobs

def job_department_code(job):
    return job['department']['code']

def job_department_description(job):
    return job['department']['description']
