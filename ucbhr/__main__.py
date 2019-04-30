# vim: set et sw=4 ts=4:

# Requires HR API credentials.

import argparse
import asyncio
import json
import logging
import os
import sys

from ucbhr import jobs, hr, info

# We use f-strings from python >= 3.6.
assert sys.version_info >= (3, 7)

# logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger('ucbhr')

secret_keys = [ 'app_id',  'app_key' ]

def has_all_keys(d, keys):
    return all (k in d for k in keys)

def read_json_data(filename, required_keys):
    '''Read and validate data from a json file.'''
    if not os.path.exists(filename):
        raise Exception(f"No such file: {filename}")
    data = json.loads(open(filename).read())
    # check that we've got all of our required keys
    if not has_all_keys(data, required_keys):
        missing = set(required_keys) - set(data.keys())
        s = f"Missing parameters in {filename}: {missing}"
        raise Exception(s)
    return data

def read_credentials(filename, required_keys=secret_keys):
    '''Read credentials from {filename}. Returns a dict.'''
    return read_json_data(filename, required_keys)

## main
async def main():
    parser = argparse.ArgumentParser(
        description="Get data from UC Berkeley's HRMS")
    parser.add_argument('-f', dest='credentials', default='ucbhr.json',
        help='credentials file.')
    parser.add_argument('-i', dest='identifier', required=True,
        help='number uniquely identifying employee')
    parser.add_argument('-t', dest='type', required=True,
        choices=['campus-uid', 'hr-employee-id', 'legacy-hr-employee-id'],
        default='campus-uid', type=str.lower, help='id type')
    parser.add_argument('-v', dest='verbose', action='store_true',
        help='set info log level')
    parser.add_argument('-d', dest='debug', action='store_true',
        help='set debug log level')

    subparsers = parser.add_subparsers(dest='command')

    jobs_parser = subparsers.add_parser('jobs', help="Get employee's jobs.")

    emails_parser = subparsers.add_parser('emails', help="Get employee's emails.")
    emails_parser.add_argument('-c', dest='code', 
        choices=['BUSN'], default='BUSN', help='email type code')

    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.INFO)
    elif args.debug:
        logger.setLevel(logging.DEBUG)
    
    # read credentials from credentials file
    credentials = read_credentials(args.credentials)
    
    if args.command == 'jobs':
        items = await jobs.get(credentials['app_id'], credentials['app_key'],
                args.identifier, args.type)
        for job in items:
            code = jobs.code(job)
            desc = jobs.description(job)
            dept_code = jobs.department_code(job)
            print(f"{dept_code}\t{code}\t{desc}")

    elif args.command == 'emails':
        items = await info.get(credentials['app_id'], credentials['app_key'],
                args.identifier, args.type)
        for email in info.emails(items, args.code): print(email)

def run():
    asyncio.run(main())
