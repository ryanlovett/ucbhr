ucbhr
=====
Query the UC Berkeley HRMS for job data.

Requires Employee API credentials.

Jobs
----
```
usage: ucbhr jobs [-h] -i IDENTIFIER -t
                  {campus-uid,hr-employee-id,legacy-hr-employee-id}

optional arguments:
  -h, --help            show this help message and exit
  -i IDENTIFIER         number uniquely identifying employee
  -t {campus-uid,hr-employee-id,legacy-hr-employee-id}
                        id type
```

Example
-------
Get waitlisted IDs for a lab section in summer 2019:

`ucbhr -d jobs -i 12345 -t campus-uid`

Get job data for person with campus UID 12345.

Credentials
-----------
Supply the credentials in a JSON file of the form:
```
{
	"app_id": "...",
	"app_key": "..."
}
```
Request credentials through [API Central](https://api-central.berkeley.edu).
