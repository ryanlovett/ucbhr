import logging
import sys

import jmespath

from . import hr

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

async def get(app_id, app_key, identifier, id_type):
    '''Return an employee's info.'''
    url = f"{hr.employees_url}/{identifier}"
    headers = {
        "Accept": "application/json",
        "app_id": app_id,
        "app_key": app_key
    }
    params = { "id-type": id_type }
    logger.debug(f"get_info: {url} {params}")
    data = await hr.get_hr_items(url, params, headers)
    logger.debug(f'info: {data}')
    return data

def emails(response, code):
    if code is None:
        expr = "emails[].emailAddress[]"
    else:
        expr = f"emails[?type.code=='{code}'].emailAddress[]"
    return jmespath.search(expr, response)
