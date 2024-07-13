# LI scrAPI for Python

API using the current endpoints on linkedin solely for scraping data without the official api.
Based entirely on [linkedin-api](https://github.com/tomquirk/linkedin-api) by Tom Quirk

Why use this library rather than the other one?
 - Async support
 - Types powered by Pydantic
 - HTTPX so we have http2 support as well
 - You don't need to interact with linkedIn but rather want data

**Caution**: This library is not officially supported by LinkedIn. Using it might violate LinkedIn's Terms of Service. Use it at your own risk.

## Installation

> Python >= 3.10 required

### Quick Start
> Script Client
```
linkedin = LinkedInScriptApi(credentials["username"], credentials["password"])
jobs = linkedin.search_jobs("Software", total_jobs = 10_000)
```

>Async Version

```
session = AsyncClient()
client = AsyncLinkedInClient(session=session)
linkedin = AsyncLinkedIn(client)
await linkedin.authenticate(credentials["username"], credentials["password"])
await linkedin.get_profile_privacy_settings("khalid-a-53a190142")
profile = await linkedin.search_people(current_company=[CompanyID.GOOGLE], past_companies=[CompanyID.APPLE], include_private_profiles=True)
company = await linkedin.get_company_updates(public_id="google")
await linkedin.get_organization("google")
jobs = await linkedin.search_jobs(
    "Software Engineer",
    sort_by=SortBy.DATE,
    location=GeoID.USA,
    remote=[LocationType.ONSITE],
    limit=10,
)
if jobs:
    for job in jobs.elements:
        job_complete = await linkedin.get_job(job.tracking_urn.split(":")[-1])
        job_skills = await linkedin.get_job_skills(job.tracking_urn.split(":")[-1])
    print(job_complete)
await linkedin.search({"keywords": "software"})
res = await linkedin.search_people(keywords="software",include_private_profiles=True)
await linkedin._close()
```

> Sync Version
```
session = Client()
client = LinkedInClient(session=session)
linkedin = LinkedIn(client)
linkedin.authenticate(credentials["username"], credentials["password"])

linkedin.get_profile_privacy_settings("khalid-a-53a190142")
profile = linkedin.search_people(current_company=[CompanyID.GOOGLE], past_companies=[CompanyID.APPLE], include_private_profiles=True)
company = linkedin.get_company_updates(public_id="google")
linkedin.get_organization("google")
jobs = linkedin.search_jobs(
    "Software Engineer",
    sort_by=SortBy.DATE,
    location=GeoID.USA,
    remote=[LocationType.ONSITE],
    limit=10,
)
if jobs:
    for job in jobs.elements:
        job_complete = linkedin.get_job(job.tracking_urn.split(":")[-1])
        job_skills = linkedin.get_job_skills(job.tracking_urn.split(":")[-1])
    print(job_complete)
linkedin.search({"keywords": "software"})
res = linkedin.search_people(keywords="software",include_private_profiles=True)
linkedin._close()
session = Client()
client = LinkedInClient(session=session)
linkedin = LinkedIn(client)
linkedin.authenticate(credentials["username"], credentials["password"])

linkedin.get_profile_privacy_settings("khalid-a-53a190142")
profile = linkedin.search_people(current_company=[CompanyID.GOOGLE], past_companies=[CompanyID.APPLE], include_private_profiles=True)
company = linkedin.get_company_updates(public_id="google")
linkedin.get_organization("google")
jobs = linkedin.search_jobs(
    "Software Engineer",
    sort_by=SortBy.DATE,
    location=GeoID.USA,
    remote=[LocationType.ONSITE],
    limit=10,
)
if jobs:
    for job in jobs.elements:
        job_complete = linkedin.get_job(job.tracking_urn.split(":")[-1])
        job_skills = linkedin.get_job_skills(job.tracking_urn.split(":")[-1])
    print(job_complete)
linkedin.search({"keywords": "software"})
res = linkedin.search_people(keywords="software",include_private_profiles=True)
linkedin._close()        session = Client()
client = LinkedInClient(session=session)
linkedin = LinkedIn(client)
linkedin.authenticate(credentials["username"], credentials["password"])

linkedin.get_profile_privacy_settings("khalid-a-53a190142")
profile = linkedin.search_people(current_company=[CompanyID.GOOGLE], past_companies=[CompanyID.APPLE], include_private_profiles=True)
company = linkedin.get_company_updates(public_id="google")
linkedin.get_organization("google")
jobs = linkedin.search_jobs(
    "Software Engineer",
    sort_by=SortBy.DATE,
    location=GeoID.USA,
    remote=[LocationType.ONSITE],
    limit=10,
)
if jobs:
    for job in jobs.elements:
        job_complete = linkedin.get_job(job.tracking_urn.split(":")[-1])
        job_skills = linkedin.get_job_skills(job.tracking_urn.split(":")[-1])
    print(job_complete)
linkedin.search({"keywords": "software"})
res = linkedin.search_people(keywords="software",include_private_profiles=True)
linkedin._close()
```

## Documentation

The examples give a quick run down of the documentation if this project takes off or gets some traction I'll make dedicated docs.
The code as well has sufficient doc strings and types to get an idea of how to interact with the code

## Disclaimer

This library is not endorsed or supported by LinkedIn. It is an unofficial library intended for educational purposes and personal use only. By using this library, you agree to not hold the author or contributors responsible for any consequences resulting from its usage.

## Contributing

Any and all contributions are helpful, if you have discovered various IDs LinkedIn uses for anything of interest make a PR and add it to the query options.

If you feel we need a new method or something to pull from LinkedIn then the following would be very helpful:
1. Add the method to the LinkedIn Interface
2. Supply the logic to both the sync and async classes
3. Add mock tests for the assumed LinkedIn response
4. add the method to the script if necessary
5. Make a PR and lets merge it in!

## Development

### Development installation

TODO

### Troubleshooting

#### I keep getting a `CHALLENGE`

Linkedin will throw you a curve ball in the form of a Challenge URL which requires Javascript to solve. Your best chance at resolution is to in on your browser use a separate library like `browser-cookie3`, getting the cookie from your browser and passing it to the API. 

#### Search problems

- Mileage may vary when searching general keywords like "software" using the standard `search` method. They've recently added some smarts around search whereby they group results by people, company, jobs etc. if the query is general enough. Try to use an entity-specific search method (i.e. search_people) where possible. Likewise if there is something you feel that should be supported please request it with a curl statement to build the request

## How it works

This project attempts to provide a simple Python interface for the Linkedin API.

> Do you mean the [legit Linkedin API](https://developer.linkedin.com/)?

NO! To retrieve structured data, the [Linkedin Website](https://linkedin.com) uses a service they call **Voyager**. Voyager endpoints give us access to pretty much everything we could want from Linkedin: profiles, companies, connections, messages, etc. - anything that you can see on linkedin.com, we can get from Voyager.

[How does it work?](#deep-dive)

### Deep dive

Voyager endpoints look like this:

```text
https://www.linkedin.com/voyager/api/identity/profileView/tom-quirk
```

Or, more clearly

```text
 ___________________________________ _______________________________
|             base path             |            resource           |
https://www.linkedin.com/voyager/api /identity/profileView/tom-quirk
```

They are authenticated with a simple cookie, which we send with every request, along with a bunch of headers.

To get a cookie, we POST a given username and password (of a valid Linkedin user account) to `https://www.linkedin.com/uas/authenticate`.


