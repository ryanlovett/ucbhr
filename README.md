ucbhr
=====
Query the UC Berkeley HRMS for job data.

Requires Employee API credentials.

Jobs
----
```
usage: ucbhr [-h] [-f CREDENTIALS] -i IDENTIFIER -t
             {campus-uid,hr-employee-id,legacy-hr-employee-id} [-v] [-d]
             {jobs,emails} ...

Get data from UC Berkeley's HRMS

positional arguments:
  {jobs,emails}
    jobs                Get employee's jobs.
    emails              Get employee's emails.

optional arguments:
  -h, --help            show this help message and exit
  -f CREDENTIALS        credentials file.
  -i IDENTIFIER         number uniquely identifying employee
  -t {campus-uid,hr-employee-id,legacy-hr-employee-id}
                        id type
  -v                    set info log level
  -d                    set debug log level
```

Example
-------
Get waitlisted IDs for a lab section in summer 2019:

`ucbhr -d -i 12345 -t campus-uid jobs`

Get job data for person with campus UID 12345.

API Access
----------
Request credentials through [API Central](https://api-central.berkeley.edu).
Supply the credentials in a JSON file of the form:
```
{
	"app_id": "...",
	"app_key": "..."
}
```
