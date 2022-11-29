# vim:set et sw=4 ts=4:
import logging
import sys

import aiohttp

import jmespath

# logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# Various SIS endpoints
employees_url = "https://gateway.api.berkeley.edu/hr/v3/employees"

async def get_hr_items(url, params, headers, item_type=None):
    '''Get a list of items (enrollments, ) from the SIS.'''
    logger.debug(f"getting {item_type}")
    data = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as r:
            if r.status == 404:
                return []
            data = await r.json()
    if item_type is None:
        return jmespath.search('response | [0]', data)
    else:
        return jmespath.search(f'response | [0].{item_type}', data)
