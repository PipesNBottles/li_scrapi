from li_scrapi import LinkedIn
from httpx import Client, Cookies, Proxy
from li_scrapi.client import LinkedInClient
from li_scrapi.utils.schemas import (
    LinkedInProfilePostsResponse,
    LinkedInPostCommentResponse,
    LinkedInUpdatesResponse,
    LinkedInJobSearchResponse,
    LinkedInSearchCompaniesResponse,
    LinkedInSearchPeopleResponse,
)
from li_scrapi.utils.query_options import (
    SortOrder,
    SortBy,
    GeoID,
    LocationType,
    JobTitle,
    JobType,
    Experience,
    CompanyID,
    NetworkDepth,
)


class LinkedInScriptApi:
    def __init__(
        self,
        username: str,
        password: str,
        cookies: Cookies | None = None,
        proxy: Proxy | None = None,
    ) -> None:
        self._linkedin = LinkedIn(
            client=LinkedInClient(session=Client(cookies=cookies, proxy=proxy))
        )
        self._linkedin.authenticate(username, password)

    def get_profile(self, public_id="", urn_id=""):
        return self._linkedin.get_profile(public_id=public_id, urn_id=urn_id)

    def get_posts_from_profile(
        self, urn_id: str, total_posts: int = 10
    ) -> list[LinkedInProfilePostsResponse]:
        res: list[LinkedInProfilePostsResponse] = []
        start = 0
        num_posts = total_posts
        current_posts = self._linkedin.get_profile_posts(urn_id, post_count=total_posts)
        if current_posts and current_posts.elements:
            res.append(current_posts)
        if total_posts > self._linkedin._MAX_POST_COUNT:
            while current_posts and current_posts.metadata.pagination_token:
                start += current_posts.paging.count
                num_posts -= current_posts.paging.count
                if total_posts <= start:
                    break

                current_posts = self._linkedin.get_profile_posts(
                    urn_id,
                    start=start,
                    post_count=num_posts,
                    pagination_token=current_posts.metadata.pagination_token,
                )
                if current_posts and current_posts.elements:
                    res.append(current_posts)

        return res

    def get_post_comments_from_post(
        self, social_detail_urn: str, sort_order=SortOrder.RELEVANCE, total_comments=100
    ) -> list[LinkedInPostCommentResponse]:
        res: list[LinkedInPostCommentResponse] = []
        start = 0
        num_comments = total_comments
        current_comments = self._linkedin.get_post_comments(
            social_detail_urn=social_detail_urn,
            sort_by=sort_order,
            comment_count=total_comments,
        )
        if current_comments and current_comments.elements:
            res.append(current_comments)
        if total_comments > self._linkedin._MAX_POST_COUNT:
            while current_comments and current_comments.metadata.pagination_token:
                start += current_comments.paging.count
                num_comments -= current_comments.paging.count
                if total_comments <= start:
                    break

                current_comments = self._linkedin.get_post_comments(
                    social_detail_urn=social_detail_urn,
                    sort_by=sort_order,
                    comment_count=num_comments,
                    start=start,
                    pagination_token=current_comments.metadata.pagination_token,
                )
                if current_comments and current_comments.elements:
                    res.append(current_comments)

        return res

    def search_jobs(
        self,
        keywords: str = "",
        companies: list[CompanyID] = [],
        experience: list[Experience] = [],
        job_type: list[JobType] = [],
        job_title: list[JobTitle] = [],
        industries: list[str] = [],
        location: GeoID | None = GeoID.USA,
        remote: list[LocationType] = [],
        listed_at=24 * 60 * 60,
        distance: int | None = None,
        sort_by: SortBy = SortBy.RELEVANCE,
        v2: bool = False,
        total_jobs=10,
    ) -> list[LinkedInJobSearchResponse]:
        res: list[LinkedInJobSearchResponse] = []
        kwargs = {
            "keywords": keywords,
            "experience": experience,
            "job_type": job_type,
            "companies": companies,
            "job_title": job_title,
            "industries": industries,
            "location": location,
            "remote": remote,
            "listed_at": listed_at,
            "distance": distance,
            "sort_by": sort_by,
            "v2": v2,
        }
        start = 0
        num_jobs = total_jobs
        all_jobs = self._linkedin.search_jobs(**kwargs, limit=total_jobs)
        if all_jobs and all_jobs.elements:
            res.append(all_jobs)
        if total_jobs > self._linkedin._MAX_SEARCH_COUNT:
            while all_jobs and all_jobs.elements:
                start += all_jobs.paging.count
                num_jobs -= all_jobs.paging.count
                if total_jobs <= start:
                    break

                all_jobs = self._linkedin.search_jobs(
                    **kwargs, limit=num_jobs, offset=start
                )
                if all_jobs and all_jobs.elements:
                    res.append(all_jobs)
        return res

    def search_people(
        self,
        keywords: str = "",
        connection_of: str = "",
        network_depths: list[NetworkDepth] = [],
        current_company: list[CompanyID] = [],
        past_companies: list[CompanyID] = [],
        nonprofit_interests: list[str] = [],
        profile_languages: list[str] = [],
        regions: list[GeoID] = [],
        industries: list[str] = [],
        schools: list[str] = [],
        service_categories: list[str] = [],
        include_private_profiles: bool = False,
        keyword_first_name: str = "",
        keyword_last_name: str = "",
        keyword_title: str = "",
        keyword_company: str = "",
        keyword_school: str = "",
        total_people: int = 10,
    ) -> list[LinkedInSearchPeopleResponse]:
        res: list[LinkedInSearchPeopleResponse] = []
        kwargs = {
            "keywords": keywords,
            "connection_of": connection_of,
            "network_depths": network_depths,
            "current_company": current_company,
            "past_companies": past_companies,
            "nonprofit_interests": nonprofit_interests,
            "profile_languages": profile_languages,
            "regions": regions,
            "industries": industries,
            "schools": schools,
            "service_categories": service_categories,
            "include_private_profiles": include_private_profiles,
            "keyword_first_name": keyword_first_name,
            "keyword_last_name": keyword_last_name,
            "keyword_title": keyword_title,
            "keyword_company": keyword_company,
            "keyword_school": keyword_school,
            "offset": 0,
        }
        start = 0
        num_people = total_people
        all_people = self._linkedin.search_people(**kwargs)
        if all_people.elements:
            res.append(all_people)
        if total_people > all_people.paging.count:
            while all_people and all_people.elements:
                start += all_people.paging.count
                num_people -= all_people.paging.count
                if total_people <= start:
                    break
                kwargs["offset"] = start
                all_people = self._linkedin.search_people(**kwargs)
                if all_people.elements:
                    res.append(all_people)

        return res

    def search_companies(
        self, keywords: str = "", total_companies=10
    ) -> list[LinkedInSearchCompaniesResponse]:
        res: list[LinkedInSearchCompaniesResponse] = []
        all_companies = self._linkedin.search_companies(keywords)
        start = 0
        num_companies = total_companies
        if all_companies.elements:
            res.append(all_companies)
        if total_companies > all_companies.paging.count:
            while all_companies and all_companies.elements:
                start += all_companies.paging.count
                num_companies -= all_companies.paging.count
                if total_companies <= start:
                    break

                all_companies = self._linkedin.search_companies(
                    keywords=keywords, offset=start
                )
                if all_companies.elements:
                    res.append(all_companies)
        return res

    def get_contact_info_from_profile(self, public_id="", urn_id=""):
        return self._linkedin.get_profile_contact_info(
            public_id=public_id, urn_id=urn_id
        )

    def get_skills_from_profile(self, public_id="", urn_id=""):
        return self._linkedin.get_profile_skills(public_id=public_id, urn_id=urn_id)

    def get_connections_from_profile(
        self, urn_id: str = "", total_connections: int = 10
    ) -> list[LinkedInSearchPeopleResponse]:
        res: list[LinkedInSearchPeopleResponse] = []
        start = 0
        num_people = total_connections
        all_connections = self._linkedin.get_profile_connections(urn_id=urn_id)
        if all_connections.elements:
            res.append(all_connections)
        if total_connections > all_connections.paging.count:
            while all_connections and all_connections.elements:
                start += all_connections.paging.count
                num_people -= all_connections.paging.count
                if total_connections <= start:
                    break
                all_connections = self._linkedin.get_profile_connections(
                    urn_id=urn_id, offset=start
                )
                if all_connections.elements:
                    res.append(all_connections)

        return res

    def get_updates_from_company(self, public_id="", urn_id="", total_posts=10):
        res: list[LinkedInUpdatesResponse] = []
        start = 0
        num_posts = total_posts
        all_updates = self._linkedin.get_company_updates(
            public_id=public_id, urn_id=urn_id, count=total_posts
        )
        if all_updates and all_updates.elements:
            res.append(all_updates)
        if total_posts > self._linkedin._MAX_UPDATE_COUNT:
            while all_updates and all_updates.elements:
                start += all_updates.paging.count
                num_posts -= all_updates.paging.count
                if total_posts <= start:
                    break

                all_updates = self._linkedin.get_company_updates(
                    public_id=public_id, urn_id=urn_id, start=start, count=num_posts
                )
                if all_updates and all_updates.elements:
                    res.append(all_updates)

        return res

    def get_updates_from_profile(self, public_id="", urn_id="", total_posts=10):
        res: list[LinkedInUpdatesResponse] = []
        start = 0
        num_posts = total_posts
        all_updates = self._linkedin.get_profile_updates(
            public_id=public_id, urn_id=urn_id, count=total_posts
        )
        if all_updates and all_updates.elements:
            res.append(all_updates)
        if total_posts > self._linkedin._MAX_UPDATE_COUNT:
            while all_updates and all_updates.elements:
                start += all_updates.paging.count
                num_posts -= all_updates.paging.count
                if total_posts <= start:
                    break

                all_updates = self._linkedin.get_profile_updates(
                    public_id=public_id, urn_id=urn_id, start=start, count=num_posts
                )
                if all_updates and all_updates.elements:
                    res.append(all_updates)

        return res

    def get_organization(self, public_id: str):
        return self._linkedin.get_organization(public_id)

    def get_user_profile(self, use_cache=True):
        return self._linkedin.get_user_profile(use_cache=use_cache)

    def get_privacy_settings_from_profile(self, public_profile_id: str):
        return self._linkedin.get_profile_privacy_settings(public_profile_id)

    def get_network_from_profile(self, public_profile_id: str):
        return self._linkedin.get_profile_network_info(public_profile_id)

    def get_job(self, job_id: str):
        return self._linkedin.get_job(job_id)

    def get_job_skills(self, job_id: str):
        return self._linkedin.get_job_skills(job_id)
