# vim: set et sw=4 ts=4:

# Requires HR API credentials.

import argparse
import asyncio
import json
import logging
import os
import sys

from ucbhr import hr

# We use f-strings from python >= 3.6.
assert sys.version_info >= (3, 7)

# logging
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logger = logging.getLogger('ucbhr')
#logger.setLevel(logging.DEBUG)

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

def filter_instructors(section, constituents):
    is_primary = sis.section_is_primary(section)
    if (is_primary and constituents == 'instructors') or \
       (not is_primary and constituents == 'gsis'):
        return sis.section_instructors(section)
        logger.info(f"exact: uids {uids}")
    return set()

def get_jobs(credentials, uid):
    '''Given a term and class section number, return the student ids.'''

    # get all enrollments for this section
    jobs = sis.get_jobs(credentials['app_id'], credentials['app_key'], uid)

    # sis codes for enrollment status
    enrollment_statuses = {'enrolled':'E', 'waitlisted':'W', 'dropped':'D'} 
    status_code = enrollment_statuses[constituents] # E, W, or D

    # extract uids from enrollments
    uids = sis.get_enrollment_uids(
        # filter enrollments by sis status code
        sis.filter_enrollment_status(enrollments, status_code)
    )

    # we convert to a set to collapse overlapping enrollments between
    # lectures and labs (if not exact)
    return set(uids)

def get_instructors(term_id, class_number, constituents, credentials, exact):
    '''Given a term and class section number, return the instructor ids.'''

    # get the data for the specified section
    section = sis.get_section_by_id(
        credentials['classes_id'], credentials['classes_key'],
        term_id, class_number, include_secondary='true'
    )

    if exact:
        uids = filter_instructors(section, constituents)
    else:
        # e.g. STAT C8
        subject_area   = sis.section_subject_area(section)
        catalog_number = sis.section_catalog_number(section)
        logger.info(f"{subject_area} {catalog_number}")

        # we search by subject area and catalog number which will return
        # all lectures, labs, discussions, etc.
        all_sections = sis.get_sections(
            credentials['classes_id'], credentials['classes_key'],
            term_id, subject_area, catalog_number
        )
        logger.info(f"num sections: {len(all_sections)}")

        uids = set()
        for section in all_sections:
            # fetch the uids of this section's instructors
            uids |= filter_instructors(section, constituents)
    return uids

def valid_term(string):
    valid_terms = ['Current', 'Next', 'Previous']
    if string.isdigit() or string in valid_terms:
        return string
    msg = f"{string} is not a term id or one of {valid_terms}"
    raise argparse.ArgumentTypeError(msg)

def csv_list(string):
   return string.split(',')

## main
async def main():
    parser = argparse.ArgumentParser(
        description="Get data from UC Berkeley's HRMS")
    parser.add_argument('-f', dest='credentials', default='ucbhr.json',
        help='credentials file.')
    parser.add_argument('-v', dest='verbose', action='store_true',
        help='set info log level')
    parser.add_argument('-d', dest='debug', action='store_true',
        help='set debug log level')

    subparsers = parser.add_subparsers(dest='command')

    jobs_parser = subparsers.add_parser('jobs',
        help='Get lists of jobs.')
    jobs_parser.add_argument('-i', dest='identifier', required=True,
        help='number uniquely identifying employee')
    jobs_parser.add_argument('-t', dest='type', required=True,
        choices=['campus-uid', 'hr-employee-id', 'legacy-hr-employee-id'],
        default='campus-uid', type=str.lower, help='id type')

    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.INFO)
    elif args.debug:
        logger.setLevel(logging.DEBUG)
    
    # read credentials from credentials file
    credentials = read_credentials(args.credentials)
    
    if args.command == 'jobs':
        print(await hr.get_jobs(credentials['app_id'], credentials['app_key'],
            args.identifier, args.type))

def run():
    asyncio.run(main())
