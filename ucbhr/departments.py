import logging
import sys

import aiohttp
import jmespath

from . import hr

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_employees(app_id, app_key, dept_code, job_types=None, hr_status="A", page_size=500):
    '''Return employee identifiers for a department.'''
    url = f"{hr.departments_url}/{dept_code}/employees"
    headers = {
        "Accept": "application/json",
        "app_id": app_id,
        "app_key": app_key
    }
    params = {
        "page-size": page_size,
        "employee-hr-status": hr_status
    }
    if job_types:
        params["job-types"] = job_types

    logger.debug(f"get_employees: {url} {params}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as r:
            if r.status == 404:
                return {"response": []}
            data = await r.json()
    logger.debug(f'employees: {data}')
    return data

def extract_campus_uids(employees_response):
    '''Extract campus-uid values from the employee list response.'''
    if not employees_response:
        return []
    return jmespath.search("response[].identifiers[?type=='campus-uid'].id", employees_response) or []
