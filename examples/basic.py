import json
from httpx import AsyncClient, Client
from li_scrapi import LinkedIn
from li_scrapi.async_linkedin import AsyncLinkedIn
from li_scrapi.client import AsyncLinkedInClient, LinkedInClient
from li_scrapi.utils.query_options import SortBy, LocationType, GeoID, CompanyID
import asyncio


async def async_main():
    if credentials:
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
        print(jobs)


def main():
    if credentials:
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


if __name__ == "__main__":
    with open("credentials.json", "r") as f:
        credentials = json.load(f)

    asyncio.run(async_main())
    main()
