# vim: set et sw=4 ts=4:

# Requires HR API credentials.

import argparse
import asyncio
import json
import logging
import os
import sys

from ucbhr import departments, jobs, hr, info

# We use f-strings from python >= 3.6.
assert sys.version_info >= (3, 7)

# logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("ucbhr")

secret_keys = ["app_id", "app_key"]


def has_all_keys(d, keys):
    return all(k in d for k in keys)


def read_json_data(filename, required_keys):
    """Read and validate data from a json file."""
    if not os.path.exists(filename):
        raise Exception(f"No such file: {filename}")
    data = json.loads(open(filename).read())
    # check that we've got all of our required keys
    if not has_all_keys(data, required_keys):
        missing = set(required_keys) - set(data.keys())
        s = f"Missing parameters in {filename}: {missing}"
        raise Exception(s)
    return data


def print_json(items):
    print(json.dumps(items, ensure_ascii=False, indent=4))


def read_credentials(filename, required_keys=secret_keys, env_prefix=None):
    """Read credentials from {filename} or env vars. Returns a dict.

    Tries the JSON credentials file first. If it doesn't exist or is missing
    keys, falls back to environment variables named {env_prefix}_ID and
    {env_prefix}_KEY. Raises if neither source provides all required keys.
    """
    if os.path.exists(filename):
        try:
            return read_json_data(filename, required_keys)
        except Exception:
            pass

    if env_prefix:
        env_creds = {}
        env_map = {
            "app_id": f"{env_prefix}_ID",
            "app_key": f"{env_prefix}_KEY",
        }
        for key in required_keys:
            env_name = env_map.get(key)
            if env_name and os.environ.get(env_name):
                env_creds[key] = os.environ[env_name]

        if len(env_creds) == len(required_keys):
            return env_creds

        missing = set(required_keys) - set(env_creds)
        if env_creds:
            raise Exception(
                f"Missing credentials via {env_prefix}_ env vars: {missing}"
            )
    else:
        missing = set(required_keys)

    if os.path.exists(filename):
        raise Exception(f"Missing parameters in {filename}: {missing}")
    if env_prefix:
        raise Exception(
            f"Credentials not found: no {filename} and no {env_prefix}_ env vars set"
        )
    raise Exception(f"Credentials not found: no {filename}")


## main
async def main():
    parser = argparse.ArgumentParser(description="Get data from UC Berkeley's HRMS")
    parser.add_argument(
        "-f", dest="credentials", default="ucbhr.json", help="api credentials file"
    )
    parser.add_argument(
        "-i",
        dest="identifier",
        help="number uniquely identifying employee",
    )
    parser.add_argument(
        "-t",
        dest="type",
        choices=["campus-uid", "hr-employee-id", "legacy-hr-employee-id"],
        default="campus-uid",
        type=str.lower,
        help="id type",
    )
    parser.add_argument(
        "-v", dest="verbose", action="store_true", help="set info log level"
    )
    parser.add_argument(
        "-d", dest="debug", action="store_true", help="set debug log level"
    )
    parser.add_argument(
        "--json", dest="as_json", action="store_true", help="output items as JSON"
    )

    subparsers = parser.add_subparsers(dest="command")

    jobs_parser = subparsers.add_parser("jobs", help="Get employee's jobs.")
    jobs_parser.add_argument(
        "-i",
        dest="identifier",
        required=True,
        help="number uniquely identifying employee",
    )
    jobs_parser.add_argument(
        "-t",
        dest="type",
        choices=["campus-uid", "hr-employee-id", "legacy-hr-employee-id"],
        default="campus-uid",
        type=str.lower,
        help="id type",
    )

    emails_parser = subparsers.add_parser("emails", help="Get employee's emails.")
    emails_parser.add_argument(
        "-i",
        dest="identifier",
        required=True,
        help="number uniquely identifying employee",
    )
    emails_parser.add_argument(
        "-t",
        dest="type",
        choices=["campus-uid", "hr-employee-id", "legacy-hr-employee-id"],
        default="campus-uid",
        type=str.lower,
        help="id type",
    )
    emails_parser.add_argument(
        "-c",
        dest="code",
        choices=["BUSN", "ALL"],
        default="BUSN",
        help="email type code",
    )

    info_parser = subparsers.add_parser("info", help="Get employee's info.")
    info_parser.add_argument(
        "-i",
        dest="identifier",
        required=True,
        help="number uniquely identifying employee",
    )
    info_parser.add_argument(
        "-t",
        dest="type",
        choices=["campus-uid", "hr-employee-id", "legacy-hr-employee-id"],
        default="campus-uid",
        type=str.lower,
        help="id type",
    )

    departments_parser = subparsers.add_parser(
        "departments", help="Get employees in a department."
    )
    departments_parser.add_argument(
        "--dept-code",
        dest="dept_code",
        required=True,
        help="HR department code (e.g. PSTAT)",
    )
    departments_parser.add_argument(
        "--job-types",
        dest="job_types",
        help="Comma-separated PPS appointment type codes",
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.INFO)
    elif args.debug:
        logger.setLevel(logging.DEBUG)

    if args.command == "departments":
        credentials = read_credentials(args.credentials, env_prefix="UCBHR_DEPARTMENTS")
        employees = await departments.get_employees(
            credentials["app_id"],
            credentials["app_key"],
            args.dept_code,
            args.job_types,
        )
        uids = departments.extract_campus_uids(employees)
        if args.as_json:
            print_json(uids)
        else:
            for uid in uids:
                print(uid)
        return

    credentials = read_credentials(args.credentials, env_prefix="UCBHR_EMPLOYEES")

    if args.command == "jobs":
        items = await jobs.get(
            credentials["app_id"], credentials["app_key"], args.identifier, args.type
        )
        if args.as_json:
            print_json(items)
        else:
            for job in items:
                code = jobs.code(job)
                desc = jobs.description(job)
                dept_code = jobs.department_code(job)
                status = jobs.status(job)
                print(f"{dept_code}\t{code}\t{desc}\t{status}")

    elif args.command == "emails":
        items = await info.get(
            credentials["app_id"], credentials["app_key"], args.identifier, args.type
        )
        logger.debug(items)
        if args.as_json:
            print_json(items.get("emails", {}))
        else:
            code = args.code
            if code == "ALL":
                code = None
            for email in info.emails(items, code):
                print(email)

    elif args.command == "info":
        items = await info.get(
            credentials["app_id"], credentials["app_key"], args.identifier, args.type
        )
        logger.debug(items)
        print_json(items)


def run():
    asyncio.run(main())

if __name__ == '__main__':
    run()
