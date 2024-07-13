"""
MIT License

Copyright (c) 2024 Tom Quirk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import http
from typing import Optional
from httpx import Cookies

from li_scrapi.utils import query_options
from li_scrapi.utils._base_linkedin import BaseLinkedIn
from li_scrapi.utils.schemas import (
    LinkedInProfile,
    LinkedInPrivacySettings,
    LinkedInMemberBadges,
    LinkedInNetwork,
    LinkedInOrganizationResponse,
    LinkedInContactInfo,
    LinkedInSearchPeopleResponse,
    LinkedInProfilePostsResponse,
    LinkedInProfileSkillsResponse,
    LinkedInPostCommentResponse,
    LinkedInSearchCompaniesResponse,
    LinkedInUpdatesResponse,
    LinkedInSelfProfile,
    LinkedInJobSearchResponse,
    LinkedInJob,
    LinkedInJobSkills,
)


class LinkedIn(BaseLinkedIn):
    """
    Class for accessing the LinkedIn API.

    :param username: Username of LinkedIn account.
    :type username: str
    :param password: Password of LinkedIn account.
    :type password: str
    """

    def _fetch(self, uri: str, base_request=False, **kwargs):
        """GET request to Linkedin API"""

        url = f"{self.client.API_BASE_URL if not base_request else self.client.LINKEDIN_BASE_URL}{uri}"
        return self.client.get(url, **kwargs)

    def _post(self, uri: str, base_request=False, **kwargs):
        """POST request to Linkedin API"""

        url = f"{self.client.API_BASE_URL if not base_request else self.client.LINKEDIN_BASE_URL}{uri}"
        return self.client.post(url, **kwargs)

    def _close(self):
        self.client.close()

    def authenticate(
        self, username: str, password: str, cookies: Optional[Cookies] = None
    ):
        if not cookies or not self.client._cookie_repository._is_token_still_valid(
            cookies.jar
        ):
            self.client.authenticate(username, password)
        else:
            self.client._set_session_cookies(cookies)
            self.client._cookie_repository.save(cookies, username)

    def get_profile_posts(
        self, urn_id: str, post_count=10, start=0, pagination_token=""
    ) -> LinkedInProfilePostsResponse | None:
        url, url_params = self._api_builder.build_profile_posts_url_params(
            urn_id,
            count=min(post_count, self._MAX_POST_COUNT),
            start=start,
            pagination_token=pagination_token,
        )
        linkedin_response = self._fetch(url, params=url_params)
        data = linkedin_response.json()
        if linkedin_response.status_code != http.HTTPStatus.OK:
            self.logger.warning(
                f"failed to get profile posts data, response: {linkedin_response.status_code}"
            )
            return None
        return LinkedInProfilePostsResponse(**data)

    def get_post_comments(
        self,
        social_detail_urn: str,
        sort_by: query_options.SortOrder = query_options.SortOrder.RELEVANCE,
        comment_count=100,
        start=0,
        pagination_token="",
    ) -> LinkedInPostCommentResponse | None:
        url, url_params = self._api_builder.build_post_comments_url_query(
            post_urn=social_detail_urn,
            count=min(comment_count, self._MAX_POST_COUNT),
            start=start,
            sort_order=sort_by.value,
            pagination_token=pagination_token,
        )
        linkedin_response = self._fetch(url, params=url_params)
        if linkedin_response.status_code != http.HTTPStatus.OK:
            self.logger.warning(
                f"failed to get post comments data, response: {linkedin_response.status_code}"
            )
            return None
        data = linkedin_response.json()

        return LinkedInPostCommentResponse(**data)

    def search(self, params: dict, offset=0) -> dict:
        url, _ = self._api_builder.build_search_url_params_query(params, offset)

        linkedin_response = self._fetch(url)

        if linkedin_response.status_code != http.HTTPStatus.OK:
            self.logger.warning(
                f"failed to get search data, response: {linkedin_response.status_code}"
            )
            return {}

        data = linkedin_response.json()

        paging = self._parse_search_data(data)

        self.logger.debug(f"results grew to {len(paging.get("elements", []))}")

        return paging

    def search_people(
        self,
        keywords: str = "",
        connection_of: str = "",
        network_depths: list[query_options.NetworkDepth] = [],
        current_company: list[query_options.CompanyID] = [],
        past_companies: list[query_options.CompanyID] = [],
        nonprofit_interests: list[str] = [],
        profile_languages: list[str] = [],
        regions: list[query_options.GeoID] = [],
        industries: list[str] = [],
        schools: list[str] = [],
        service_categories: list[str] = [],
        include_private_profiles=False,  # profiles without a public id, "Linkedin Member"
        keyword_first_name: str = "",
        keyword_last_name: str = "",
        keyword_title: str = "",
        keyword_company: str = "",
        keyword_school: str = "",
        offset: int = 0,
    ) -> LinkedInSearchPeopleResponse:
        kwargs = {
            "connection_of": connection_of,
            "network_depths": [depth.value for depth in network_depths],
            "regions": [f"{region.value}" for region in regions],
            "industries": industries,
            "current_company": [f"{company.value}" for company in current_company],
            "past_companies": [f"{company.value}" for company in past_companies],
            "profile_languages": profile_languages,
            "nonprofit_interests": nonprofit_interests,
            "schools": schools,
            "service_categories": service_categories,
            "keyword_first_name": keyword_first_name,
            "keyword_last_name": keyword_last_name,
            "keyword_title": keyword_title,
            "keyword_company": keyword_company,
            "keyword_school": keyword_school,
        }

        params = self._api_builder.build_search_people_params(**kwargs)

        if keywords:
            params["keywords"] = keywords

        data = self.search(params, offset=offset)

        results = self._normalize_search_people_data(data, include_private_profiles)
        data["elements"] = results
        return LinkedInSearchPeopleResponse(**data)

    def search_companies(
        self, keywords: str = "", offset: int = 0
    ) -> LinkedInSearchCompaniesResponse:
        params = self._api_builder.build_search_companies_params(keywords)

        data = self.search(params, offset=offset)

        results = self._normalize_search_company_data(data)
        data["elements"] = results

        return LinkedInSearchCompaniesResponse(**data)

    def search_jobs(
        self,
        keywords: str = "",
        companies: list[query_options.CompanyID] = [],
        experience: list[query_options.Experience] = [],
        job_type: list[query_options.JobType] = [],
        job_title: list[query_options.JobTitle] = [],
        industries: list[str] = [],
        location: query_options.GeoID | None = None,
        remote: list[query_options.LocationType] = [],
        listed_at=24 * 60 * 60,
        distance: int | None = None,
        sort_by: query_options.SortBy = query_options.SortBy.RELEVANCE,
        v2: bool = False,
        limit=10,
        offset=0,
    ) -> LinkedInJobSearchResponse | None:
        count = min(limit, self._MAX_SEARCH_COUNT)

        kwargs = {
            "keywords": keywords,
            "experience": [f"{exp.value}" for exp in experience],
            "jobType": [job.value for job in job_type],
            "workplaceType": [f"{rem.value}" for rem in remote],
            "locationUnion": f"{location.value}" if location else "",
            "company": [f"{company.value}" for company in companies],
            "title": [f"{title.value}" for title in job_title],
            "industry": industries,
            "distance": distance,
            "sortBy": sort_by.value,
            "timePostedRange": listed_at,
        }

        url, _ = self._api_builder.build_search_jobs_url_query(count, offset, **kwargs)

        headers = {}
        if v2:
            headers = self._api_builder.get_v2_headers()

        linkedin_response = self._fetch(url, headers=headers, timeout=10.0)

        if linkedin_response.status_code != http.HTTPStatus.OK:
            self.logger.warning(
                f"failed to get jobs, response: {linkedin_response.status_code}"
            )
            return None

        data = linkedin_response.json()

        paging = self._normalize_search_jobs_data(data, v2)

        self.logger.debug(f"Collected {paging["paging"]["count"]} jobs")

        return LinkedInJobSearchResponse(**paging)

    def get_profile_contact_info(
        self, public_id: str = "", urn_id: str = ""
    ) -> LinkedInContactInfo | None:
        if not public_id and not urn_id:
            self.logger.info("Need to specifiy either a public id or a urn id")
            return None

        url = self._api_builder.build_contact_info_url(public_id, urn_id)
        res = self._fetch(url)
        data = res.json()

        contact_info = self._normalize_contact_info(data)

        return LinkedInContactInfo(**contact_info)

    def get_profile_skills(
        self, public_id: str = "", urn_id: str = ""
    ) -> LinkedInProfileSkillsResponse | None:
        if not public_id and not urn_id:
            self.logger.info("Need either public id or urn id to continue")
            return None

        params = self._api_builder.get_default_params()
        url = self._api_builder.build_skills_info_url(public_id, urn_id)
        linkedin_response = self._fetch(url, params=params)

        if linkedin_response.status_code != http.HTTPStatus.OK:
            self.logger.warning(
                f"failed to get profile skills, response: {linkedin_response.status_code}"
            )
            return None

        data = linkedin_response.json()

        return LinkedInProfileSkillsResponse(**data)

    def get_profile(
        self, public_id: str = "", urn_id: str = ""
    ) -> LinkedInProfile | None:
        if not public_id and not urn_id:
            self.logger.info("Need either public id or urn id to continue")
            return None

        url = self._api_builder.build_get_profile_url(public_id, urn_id)
        linkedin_response = self._fetch(url)

        if linkedin_response.status_code != http.HTTPStatus.OK:
            self.logger.warning(
                f"failed to get profile data, response: {linkedin_response.status_code}"
            )
            return None

        data = linkedin_response.json()

        # massage [profile] data
        profile = self._normalize_person_data(data)

        return LinkedInProfile(**profile)

    def get_profile_connections(
        self, urn_id: str, offset: int = 0
    ) -> LinkedInSearchPeopleResponse:
        return self.search_people(
            connection_of=urn_id,
            network_depths=[query_options.NetworkDepth.FIRST],
            offset=offset,
        )

    def get_company_updates(
        self,
        public_id: str = "",
        urn_id: str = "",
        start: int = 0,
        count: int = BaseLinkedIn._MAX_UPDATE_COUNT,
    ) -> LinkedInUpdatesResponse | None:
        if not public_id and not urn_id:
            self.logger.info("Need either public id or urn id to continue")
            return None

        url, params = self._api_builder.build_company_updates_url_params(
            public_id, urn_id, min(count, self._MAX_UPDATE_COUNT), start
        )

        linkedin_response = self._fetch(url, params=params)

        if linkedin_response.status_code != http.HTTPStatus.OK:
            self.logger.warning(
                f"Failed to collect company data, error code: {linkedin_response.status_code}"
            )
            return None

        data = linkedin_response.json()
        paging = data["paging"]
        paging["elements"] = data["elements"]

        self.logger.debug(f"results grew: {data["paging"]["count"]}")

        return LinkedInUpdatesResponse(paging=data["paging"], elements=data["elements"])

    def get_profile_updates(
        self,
        public_id: str = "",
        urn_id: str = "",
        start: int = 0,
        count: int = BaseLinkedIn._MAX_UPDATE_COUNT,
    ):
        if not public_id and not urn_id:
            self.logger.info("Need either public id or urn id to continue")
            return None

        url, params = self._api_builder.build_profile_updates_url_params(
            public_id, urn_id, min(count, self._MAX_UPDATE_COUNT), start
        )

        linkedin_response = self._fetch(url, params=params)

        if linkedin_response.status_code != http.HTTPStatus.OK:
            self.logger.warning(
                f"failed to get profile updates, response: {linkedin_response.status_code}"
            )
            return None

        data = linkedin_response.json()
        return LinkedInUpdatesResponse(**data)

    def get_organization(self, public_id: str):
        url, params = self._api_builder.build_get_organization_url_params(public_id)

        linkedin_response = self._fetch(url, params=params)

        if linkedin_response.status_code != http.HTTPStatus.OK:
            self.logger.warning(
                f"failed to get organization data, response: {linkedin_response.status_code}"
            )
            return None

        data = linkedin_response.json()
        paging = data["paging"]
        elements = data["elements"][0]

        return LinkedInOrganizationResponse(paging=paging, elements=elements)

    def get_user_profile(self, use_cache=True) -> LinkedInSelfProfile | None:
        me_profile = self._metadata.get("me")
        if not me_profile and (not self.client.metadata.get("me") or not use_cache):
            linkedin_response = self._fetch("/me")

            if linkedin_response.status_code != http.HTTPStatus.OK:
                self.logger.warning(
                    f"failed to get user profile data, response: {linkedin_response.status_code}"
                )
                return me_profile

            me_profile = LinkedInSelfProfile(**linkedin_response.json())
            # cache profile
            self._metadata["me"] = me_profile

        return me_profile

    def get_profile_privacy_settings(self, public_profile_id: str):
        res = self._fetch(
            self._api_builder.build_privacy_settings_url(public_profile_id),
            headers=self._api_builder.get_v2_headers(),
        )
        if res.status_code != http.HTTPStatus.OK:
            return None

        data = res.json()
        return LinkedInPrivacySettings(**data.get("data", {}))

    def get_profile_member_badges(self, public_profile_id: str):
        res = self._fetch(
            self._api_builder.build_member_badges_url(public_profile_id),
            headers=self._api_builder.get_v2_headers(),
        )
        if res.status_code != http.HTTPStatus.OK:
            return None

        data = res.json()
        return LinkedInMemberBadges(**data.get("data", {}))

    def get_profile_network_info(self, public_profile_id: str):
        res = self._fetch(
            self._api_builder.build_profile_network_url(public_profile_id),
            headers=self._api_builder.get_v2_headers(),
        )
        if res.status_code != http.HTTPStatus.OK:
            return None

        data = res.json()
        return LinkedInNetwork(**data.get("data", {}))

    def get_job(self, job_id: str) -> LinkedInJob | None:
        url, params = self._api_builder.build_get_job_url_params(job_id)

        linkedin_response = self._fetch(url, params=params)

        if linkedin_response.status_code != http.HTTPStatus.OK:
            self.logger.warning(
                f"failed to get job data, response: {linkedin_response.status_code}"
            )
            return None

        data = linkedin_response.json()
        data["workplaceTypes"] = [
            query_options.LocationType(int(val.split(":")[-1]))
            for val in data["workplaceTypes"]
        ]

        return LinkedInJob(**data)

    def get_job_skills(self, job_id: str) -> LinkedInJobSkills | None:
        url, params = self._api_builder.build_get_job_skill_url_params(job_id)
        linkedin_response = self._fetch(
            url,
            params=params,
        )
        if linkedin_response.status_code != http.HTTPStatus.OK:
            self.logger.warning(
                f"failed to get job data, response: {linkedin_response.status_code}"
            )
            return None

        data = linkedin_response.json()

        return LinkedInJobSkills(**data)
