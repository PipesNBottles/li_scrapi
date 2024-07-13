import pytest
import pytest_asyncio
import httpx
import respx

from li_scrapi.async_linkedin import AsyncLinkedIn
from li_scrapi.client import AsyncLinkedInClient
from li_scrapi.utils.query_options import SortBy, LocationType, GeoID


TEST_PROFILE_ID = "TEST_PROFILE_ID"
TEST_PUBLIC_PROFILE_ID = "TEST_PUBLIC_PROFILE_ID"
TEST_CONVERSATION_ID = "TEST_CONVERSATION_ID"
TEST_COMMENT_ID = "TEST_COMMENT_ID"


@pytest_asyncio.fixture
@respx.mock
async def init_linkedin(respx_mock):
    client = httpx.AsyncClient()
    linkedin_client = AsyncLinkedInClient(session=client)
    linkedin = AsyncLinkedIn(linkedin_client)
    payload = {
        "session_key": "foo",
        "session_password": "bar",
        "JSESSIONID": "hello world",
    }
    respx_mock.get(f"{linkedin_client.LINKEDIN_BASE_URL}/uas/authenticate").respond(
        status_code=200, cookies={"JSESSIONID": "hello world"}
    )
    respx_mock.post(
        f"{linkedin_client.LINKEDIN_BASE_URL}/uas/authenticate",
        data=payload,
        headers=linkedin_client.AUTH_REQUEST_HEADERS,
        cookies=linkedin_client._session.cookies,
    ).mock(return_value=httpx.Response(status_code=200, json={"login_result": "PASS"}))
    respx_mock.get(f"{linkedin_client.LINKEDIN_BASE_URL}")
    await linkedin.authenticate("foo", "bar")
    return linkedin


@pytest.mark.asyncio
@respx.mock
async def test_get_profile(init_linkedin):
    mock_json_response = {
        "profile": {
            "industryName": "Test Data",
            "lastName": "Doles",
            "locationName": "Earth",
            "student": True,
            "geoCountryName": "Spain",
            "geoCountryUrn": "yee haw",
            "industryUrn": "yippie",
            "firstName": "Bob",
            "entityUrn": "uhhhh",
            "geoLocationName": "Texas wey",
            "headline": "thats how we do it",
            "urn_id": "1234",
            "profile_urn": "test",
            "member_urn": "test",
            "public_id": "test",
        },
        "positionView": {
            "elements": [],
        },
        "educationView": {
            "elements": [],
        },
        "languageView": {
            "elements": [],
        },
        "skillView": {
            "elements": [],
        },
        "publicationView": {
            "elements": [],
        },
        "certificationView": {
            "elements": [],
        },
        "volunteerExperienceView": {
            "elements": [],
        },
        "honorView": {
            "elements": [],
        },
        "projectView": {
            "elements": [],
        },
        "entityUrn": "hello world",
    }
    respx.get(
        init_linkedin.client.API_BASE_URL
        + f"/identity/profiles/{TEST_PROFILE_ID}/profileView"
    ).mock(return_value=httpx.Response(status_code=200, json=mock_json_response))
    profile = await init_linkedin.get_profile(urn_id=TEST_PROFILE_ID)

    assert profile is not None


@pytest.mark.asyncio
@respx.mock
async def test_get_profile_privacy_settings(init_linkedin):
    mock_json_response = {
        "data": {
            "messagingTypingIndicators": "ALL_ENABLED",
            "allowOpenProfile": True,
            "profilePictureVisibilitySetting": "PUBLIC",
            "entityUrn": "hello world",
            "showPublicProfile": True,
            "showPremiumSubscriberBadge": True,
            "publicProfilePictureVisibilitySetting": "PUBLIC",
            "formerNameVisibilitySetting": "PUBLIC",
            "messagingSeenReceipts": "ALL_ENABLED",
            "allowProfileEditBroadcasts": True,
        },
    }
    respx.get(
        init_linkedin.client.API_BASE_URL
        + f"/identity/profiles/{TEST_PUBLIC_PROFILE_ID}/privacySettings"
    ).mock(return_value=httpx.Response(status_code=200, json=mock_json_response))
    data = await init_linkedin.get_profile_privacy_settings(TEST_PUBLIC_PROFILE_ID)

    assert data is not None


@pytest.mark.asyncio
@respx.mock
async def test_get_profile_member_badges(init_linkedin):
    mock_json_response = {
        "data": {
            "premium": True,
            "influencer": True,
            "entityUrn": "hello world",
            "openLink": True,
            "jobSeeker": True,
        },
    }
    respx.get(
        init_linkedin.client.API_BASE_URL
        + f"/identity/profiles/{TEST_PUBLIC_PROFILE_ID}/memberBadges"
    ).mock(return_value=httpx.Response(status_code=200, json=mock_json_response))
    data = await init_linkedin.get_profile_member_badges(TEST_PUBLIC_PROFILE_ID)
    assert data is not None


@pytest.mark.asyncio
@respx.mock
async def test_get_profile_network_info(init_linkedin):
    mock_json_response = {
        "data": {
            "distance": {"value": "DISTANCE_3"},
            "entityUrn": "hello world",
            "following": False,
            "followable": False,
            "*followingInfo": "hello world",
            "followersCount": 100,
            "connectionsCount": 100,
        }
    }
    respx.get(
        init_linkedin.client.API_BASE_URL
        + f"/identity/profiles/{TEST_PUBLIC_PROFILE_ID}/networkinfo"
    ).mock(return_value=httpx.Response(status_code=200, json=mock_json_response))
    data = await init_linkedin.get_profile_network_info(TEST_PUBLIC_PROFILE_ID)
    assert data is not None


@pytest.mark.asyncio
@respx.mock
async def test_get_profile_contact_info(init_linkedin):
    mock_json_response = {
        "emailAddress": "foo@bar.com",
        "twitterHandles": [{"name": "foobydoobydoo", "credentialId": "tyest"}],
        "birthDateOn": {"month": 10, "day": 31},
    }
    respx.get(
        init_linkedin.client.API_BASE_URL
        + f"/identity/profiles/{TEST_PROFILE_ID}/profileContactInfo"
    ).mock(return_value=httpx.Response(status_code=200, json=mock_json_response))
    contact_info = await init_linkedin.get_profile_contact_info(TEST_PROFILE_ID)
    assert contact_info


@pytest.mark.asyncio
@respx.mock
async def test_get_profile_posts(init_linkedin):
    mock_json_response = {
        "metadata": {
            "paginationToken": "asadsfsfw",
        },
        "elements": [
            {
                "actor": {
                    "urn": "urn:li:member:229062566",
                    "image": {},
                    "supplementaryActorInfo": {},
                    "name": {},
                    "subDescription": {},
                    "navigationContext": {},
                    "description": {},
                    "followAction": {},
                },
                "dashEntityUrn": "urn:li:fsd_update:(urn:li:activity:7216537517385244672,MEMBER_SHARES,EMPTY,DEFAULT,false)",
                "updateMetadata": {
                    "urn": "urn:li:activity:7216537517385244672",
                    "actionsPosition": "ACTOR_COMPONENT",
                    "updateActions": {},
                    "actionTriggerEnabled": False,
                    "detailPageType": "FEED_DETAIL",
                    "shareAudience": "PUBLIC",
                    "shareUrn": "urn:li:share:7216537516877783041",
                    "excludedFromSeen": False,
                    "rootShare": True,
                    "trackingData": {},
                },
                "socialContent": {
                    "updateSaveActionToolTipLegoTrackingToken": "0NfmlWqldVomNMsSBA9z0Kc3RBsCZzkTsCfn9xk6NBkDsCfmhLjmNBkDsCcjRApnhPpnlNpl9JtmUCjAZ9l4BjjR0Zuk9OpmhOjThBpShFtOpApmlCnSVFomRvrCZFt6dxnSlSoncZp4BQpmtAqnsCc3RKrSBQqndLk7hBpShFtOoMbz0Zpn9LoRdOpOoZsC5gr6lisCsCfmhLjmNBkD9D9z0ZrCZFt6BPrR1MtmZOpOoNfmhBt7dBtn5BkCRRjD1RrT9D9CVLqnhzolZBtC5Pfmh9s7lLsCsCjAZ9l4BjjR0Zuk9OpmhOrOpQr7lxpClAfmh9t6VBrmtBsOpQr7lxpClAfmh9t6ZIsOpQr7lxpClAfmh9t7lLum5I9DdQrClJqn9Bs7xBnT9xoBZIomBzrTdvp6lBpzRBrm5epmtxs2pOpmtxumZSfmh9s71x9zgNcj0PcjRAimVLqndOpnoCdz8RdjkPej0Vfmh9tioTe6cTpC8Up6kQc6gJczkUeiQMejgQbj8ScjkJcm4PcPoTcCcZp4BQu6lQrCZz",
                    "shareUrl": "https://www.linkedin.com/posts/joekerridge_angular-hiring-ecommerce-activity-7216537517385244672-vImc?utm_source=combined_share_message&utm_medium=member_desktop",
                },
                "entityUrn": "urn:li:fs_updateV2:(urn:li:activity:7216537517385244672,MEMBER_SHARES,EMPTY,DEFAULT,false)",
                "commentary": {
                    "numLines": 3,
                    "text": {"text": "This is why we parse with pydantic"},
                },
                "socialDetail": {
                    "reactionElements": [],
                    "dashEntityUrn": "urn:li:fsd_socialDetail:(urn:li:activity:7216537517385244672,urn:li:activity:7216537517385244672,urn:li:highlightedReply:-)",
                    "comments": {},
                    "socialPermissions": {},
                    "showPremiumAnalytics": False,
                    "hideFirstPrompt": True,
                    "liked": False,
                    "showShareButton": True,
                    "totalShares": 3,
                    "urn": "urn:li:activity:7216537517385244672",
                    "threadId": "activity:7216537517385244672",
                    "allowedCommentersScope": "ALL",
                    "totalSocialActivityCounts": {},
                    "entityUrn": "urn:li:fs_socialDetail:urn:li:activity:7216537517385244672",
                    "commentingDisabled": False,
                    "likes": {
                        "paging": {
                            "count": 0,
                            "total": 10,
                            "start": 100,
                        }
                    },
                },
            }
        ],
        "paging": {"count": 10, "start": 0, "links": []},
    }
    respx.get(init_linkedin.client.API_BASE_URL + "/identity/profileUpdatesV2").mock(
        return_value=httpx.Response(status_code=200, json=mock_json_response)
    )
    posts = await init_linkedin.get_profile_posts(TEST_PROFILE_ID)
    assert posts


@pytest.mark.asyncio
@respx.mock
async def test_get_post_comments(init_linkedin):
    mock_json_response = {
        "metadata": {
            "paginationToken": "assdfsdfqw"
        },
        "paging": {"count": 100, "start": 0, "total": 3, "links": []},
        "elements": [
            {
                "commenterProfileId": "ACoAACHl0w8BXs6TP9uVAUKMIO-wKHHD8jqlExQ",
                "dashEntityUrn": "urn:li:fsd_comment:(7216546708355211265,urn:li:activity:7216537517385244672)",
                "pinned": False,
                "edited": False,
                "index": -1,
                "commenterForDashConversion": {
                    "urn": "urn:li:member:568709903",
                    "image": {},
                    "commenterProfileId": "ACoAACHl0w8BXs6TP9uVAUKMIO-wKHHD8jqlExQ",
                    "supplementaryActorInfoV2": {},
                    "author": False,
                    "subtitle": "Frontend Engineer / Fullstack Engineer / Senior Software Engineer | MS CS @ UC-Riverside | Ex - UII-AH | Ex-Quinbay | Ex-piMonk | Ex - Mu-Sigma",
                    "actorUnion": {},
                    "navigationUrl": "https://www.linkedin.com/in/deepak-urs",
                    "title": {},
                    "trackingActionType": "viewMember",
                    "accessibilityText": "View Deepak Urs’ profile",
                },
                "timeOffset": -1,
                "originalLanguage": "English",
                "commenter": {"com.linkedin.voyager.feed.MemberActor": {}},
                "socialDetail": {
                    "urn": "urn:li:comment:(activity:7216537517385244672,7216546708355211265)",
                    "threadId": "comment:(activity:7216537517385244672,7216546708355211265)",
                    "allowedCommentersScope": "ALL",
                    "dashEntityUrn": "urn:li:fsd_socialDetail:(urn:li:comment:(activity:7216537517385244672,7216546708355211265),urn:li:comment:(activity:7216537517385244672,7216546708355211265),urn:li:highlightedReply:-)",
                    "comments": {},
                    "totalSocialActivityCounts": {},
                    "socialPermissions": {},
                    "entityUrn": "urn:li:fs_socialDetail:urn:li:comment:(activity:7216537517385244672,7216546708355211265)",
                    "hideFirstPrompt": True,
                    "liked": False,
                    "showShareButton": False,
                    "likes": {
                        "paging": {
                            "total": 100,
                            "start": 0,
                            "count": 100,
                        }
                    },
                },
                "urn": "urn:li:comment:(activity:7216537517385244672,7216546708355211265)",
                "threadId": "activity:7216537517385244672",
                "entityUrn": "urn:li:fs_objectComment:(7216546708355211265,activity:7216537517385244672)",
                "hideCommentAction": {
                    "hideTrackingActionType": "hideComment",
                    "dashEntityUrn": "urn:li:fsd_hideCommentAction:urn:li:fsd_comment:(7216546708355211265,urn:li:activity:7216537517385244672)",
                    "entityUrn": "urn:li:fs_hideCommentAction:urn:li:fs_objectComment:(7216546708355211265,activity:7216537517385244672)",
                },
                "commentV2": {
                    "textDirection": "FIRST_STRONG",
                    "attributes": [],
                    "text": "Thank you for the post Joe Kerridge! My skills and experience as a former 'Senior Software Engineer(Frontend)’ strongly resonates with the ‘Senior Frontend Engineer’ role.\n\nIn addition, I’ve emailed and PMed you my necessary details for your quick reference and have sent you a linkedIn connection request to\xa0discuss and know more about the role from you. Please accept it, thanks in advance!",
                },
                "createdTime": 1720558812226,
                "canDelete": False,
                "comment": {"values": []},
                "permalink": "https://www.linkedin.com/feed/update/urn:li:activity:7216537517385244672?commentUrn=urn%3Ali%3Acomment%3A%28activity%3A7216537517385244672%2C7216546708355211265%29&dashCommentUrn=urn%3Ali%3Afsd_comment%3A%287216546708355211265%2Curn%3Ali%3Aactivity%3A7216537517385244672%29",
                "actions": ["SHARE_VIA", "REPORT", "HIDE"],
                "contributed": False,
                "trackingId": "mYrL5sKsScFNkW4Ryzaaaw==",
            }
        ],
    }
    respx.get(init_linkedin.client.API_BASE_URL + "/feed/comments").mock(
        return_value=httpx.Response(status_code=200, json=mock_json_response)
    )
    comments = await init_linkedin.get_post_comments(TEST_COMMENT_ID)
    assert comments


@pytest.mark.asyncio
@respx.mock
async def test_get_organization(init_linkedin):
    mock_json_response = {
        "paging": {
            "count": 10,
            "start": 0,
        },
        "elements": [
            {
                "staffingCompany": True,
                "staffCount": 0,
                "adsRule": "hello world",
                "claimable": True,
                "lcpTreatment": True,
                "name": "Harvard Medical School",
                "description": "hello world",
                "paidCompany": True,
                "companyPageUrl": "https://httpbin.org",
                "url": "https://httpbin.org",
                "jobSearchPageUrl": "https://httpbin.org",
                "specialities": ["hello", "woeld"],
                "companyIndustries": [{"localizedName": "test"}],
                "headquarter": {
                    "country": "US",
                    "geographicArea": "CA",
                    "city": "San Andreas",
                    "line1": "hellow word",
                },
                "confirmedLocations": [
                    {
                        "country": "US",
                        "geographicArea": "CA",
                        "city": "San Andreas",
                        "line1": "hellow word",
                    }
                ],
            }
        ],
    }
    respx.get(
        init_linkedin.client.API_BASE_URL + "/organization/companies",
        params={"universalName": "harvard-medical-school"},
    ).mock(return_value=httpx.Response(status_code=200, json=mock_json_response))
    data = await init_linkedin.get_organization("harvard-medical-school")
    assert data is not None
    assert data.elements.name == "Harvard Medical School"


@pytest.mark.asyncio
@respx.mock
async def test_search_people(init_linkedin):
    mock_json_response = {
        "data": {
            "searchDashClustersByAll": {
                "_type": "com.linkedin.restli.common.CollectionResponse",
                "paging": {
                    "count": 10,
                    "start": 0,
                    "_type": "com.linkedin.restli.common.CollectionMetadata",
                    "total": 1000,
                    "_recipeType": "com.linkedin.81b214c2cdd4f02cdb7d827958d2f3a1",
                },
                "_recipeType": "com.linkedin.5f1d22f924ecb6a031ee124b8b767900",
                "elements": [
                    {
                        "image": None,
                        "quickFilterActions": [],
                        "clusterRenderType": "LIST",
                        "dismissable": False,
                        "totalResultCount": None,
                        "_type": "com.linkedin.voyager.dash.search.SearchClusterViewModel",
                        "controlName": None,
                        "description": None,
                        "_recipeType": "com.linkedin.5c853aba2154c55483e72bf6cdfaaf3e",
                        "title": None,
                        "actionTypeName": None,
                        "navigationText": None,
                        "feature": None,
                        "navigationCardAction": None,
                        "position": 1,
                        "items": [
                            {
                                "template": "UNIVERSAL",
                                "actorNavigationContext": None,
                                "trackingUrn": "urn:li:member:912343735",
                                "controlName": None,
                                "interstitialComponent": None,
                                "primaryActions": [],
                                "entityCustomTrackingInfo": {
                                    "memberDistance": "DISTANCE_2",
                                    "_type": "com.linkedin.voyager.dash.search.EntityCustomTrackingInfo",
                                    "privacySettingsInjectionHolder": None,
                                    "_recipeType": "com.linkedin.4caf791202c7b71e3874d4551f078f32",
                                    "nameMatch": False,
                                },
                                "title": {
                                    "textDirection": "FIRST_STRONG",
                                    "_type": "com.linkedin.voyager.dash.common.text.TextViewModel",
                                    "text": "Ryan Pham",
                                    "attributesV2": [],
                                    "_recipeType": "com.linkedin.6a224ca38654a84754a1eb3e97c0f846",
                                    "accessibilityTextAttributesV2": [],
                                    "accessibilityText": "View Ryan Pham’s profile",
                                },
                                "overflowActions": [],
                                "searchActionType": None,
                                "actorInsights": [],
                                "insightsResolutionResults": [{}],
                                "badgeIcon": None,
                                "entityUrn": "urn:li:fsd_entityResultViewModel:(urn:li:fsd_profile:ACoAADZhQrcBOnO0-ZuGBZFS-h6YJNrbW_NiZKM,SEARCH_SRP,DEFAULT)",
                                "showAdditionalCluster": False,
                                "ringStatus": None,
                                "primarySubtitle": {
                                    "textDirection": "USER_LOCALE",
                                    "_type": "com.linkedin.voyager.dash.common.text.TextViewModel",
                                    "text": "Software Development & Analytics",
                                    "attributesV2": [],
                                    "_recipeType": "com.linkedin.6a224ca38654a84754a1eb3e97c0f846",
                                    "accessibilityTextAttributesV2": [],
                                    "accessibilityText": None,
                                },
                                "badgeText": {
                                    "textDirection": "USER_LOCALE",
                                    "_type": "com.linkedin.voyager.dash.common.text.TextViewModel",
                                    "text": "• 2nd",
                                    "attributesV2": [],
                                    "_recipeType": "com.linkedin.6a224ca38654a84754a1eb3e97c0f846",
                                    "accessibilityTextAttributesV2": [],
                                    "accessibilityText": "2nd degree connection",
                                },
                                "trackingId": "stBykACtTRS7AIjfIbJbzw==",
                                "summary": {
                                    "textDirection": "USER_LOCALE",
                                    "_type": "com.linkedin.voyager.dash.common.text.TextViewModel",
                                    "text": "Current: Software Engineer at Trace",
                                    "attributesV2": [],
                                    "_recipeType": "com.linkedin.6a224ca38654a84754a1eb3e97c0f846",
                                    "accessibilityTextAttributesV2": [],
                                    "accessibilityText": None,
                                },
                                "addEntityToSearchHistory": True,
                                "actorNavigationUrl": None,
                                "image": {
                                    "_type": "com.linkedin.voyager.dash.common.image.ImageViewModel",
                                    "attributes": [],
                                    "actionTarget": None,
                                    "_recipeType": "com.linkedin.fe5b8a3ac5a4a165c17f53b7eae4209b",
                                    "accessibilityTextAttributes": [],
                                    "totalCount": None,
                                    "accessibilityText": "Ryan Pham",
                                },
                                "lazyLoadedActions": {
                                    "_recipeType": "com.linkedin.92ece182782ae4412e712925cd97f9fe",
                                    "_type": "com.linkedin.voyager.dash.search.LazyLoadedActions",
                                    "entityUrn": "urn:li:fsd_lazyLoadedActions:(urn:li:fsd_profileActions:(ACoAADZhQrcBOnO0-ZuGBZFS-h6YJNrbW_NiZKM,SEARCH,EMPTY_CONTEXT_ENTITY_URN),PEOPLE,SEARCH_SRP)",
                                },
                                "secondarySubtitle": {
                                    "textDirection": "USER_LOCALE",
                                    "_type": "com.linkedin.voyager.dash.common.text.TextViewModel",
                                    "text": "Garden Grove, CA",
                                    "attributesV2": [],
                                    "_recipeType": "com.linkedin.6a224ca38654a84754a1eb3e97c0f846",
                                    "accessibilityTextAttributesV2": [],
                                    "accessibilityText": None,
                                },
                                "_type": "com.linkedin.voyager.dash.search.EntityResultViewModel",
                                "navigationUrl": "https://www.linkedin.com/in/ryantpham?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAADZhQrcBOnO0-ZuGBZFS-h6YJNrbW_NiZKM",
                                "entityEmbeddedObject": None,
                                "unreadIndicatorDetails": None,
                                "_recipeType": "com.linkedin.cf4b25c18907ea8eafe915c8bfa24109",
                                "target": None,
                                "actorTrackingUrn": None,
                                "navigationContext": {
                                    "_type": "com.linkedin.voyager.dash.search.NavigationContext",
                                    "openExternally": False,
                                    "_recipeType": "com.linkedin.55ee9afd4182671fe7e271f615659525",
                                    "url": "https://www.linkedin.com/in/ryantpham?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAADZhQrcBOnO0-ZuGBZFS-h6YJNrbW_NiZKM",
                                },
                            }
                        ],
                        "results": [],
                    }
                ],
            }
        }
    }
    url = "/graphql?variables=(start:0,origin:GLOBAL_SEARCH_HEADER,query:(keywords:software,flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.b0928897b71bd00a5a7291755dcd64f0"
    respx.get(init_linkedin.client.API_BASE_URL + url).mock(
        return_value=httpx.Response(status_code=200, json=mock_json_response)
    )
    results = await init_linkedin.search_people(
        keywords="software",
        include_private_profiles=True,
    )
    assert results


@pytest.mark.asyncio
@respx.mock
async def test_search_jobs_v1(init_linkedin):
    mock_json_response = {
        "paging": {
            "total": 698,
            "start": 0,
            "count": 10,
            "links": [],
            "$recipeType": "com.linkedin.voyager.dash.deco.common.FullPaging",
        },
        "elements": [
            {
                "jobCardUnion": {
                    "jobPostingCard": {
                        "jobPosting": {
                            "contentSource": "JOBS_PREMIUM_OFFLINE",
                            "entityUrn": "urn:li:fsd_jobPosting:3967499755",
                            "trackingUrn": "urn:li:jobPosting:3967499755",
                            "$recipeType": "com.linkedin.deco.recipe.anonymous.Anon1578943416",
                            "repostedJob": True,
                            "title": "Python Developer",
                            "posterId": "703343244",
                        }
                    }
                },
                "$recipeType": "com.linkedin.deco.recipe.anonymous.Anon1964842452",
            }
        ],
    }
    url = "/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-174&count=10&q=jobSearch&query=(origin:JOB_SEARCH_PAGE_QUERY_EXPANSION,selectedFilters:(workplaceType:List(1),sortBy:List(DD),timePostedRange:List(r86400)),spellCorrectionEnabled:true,keywords:Software+Engineer,locationUnion:(geoId:103644278))&start=0"
    respx.get(init_linkedin.client.API_BASE_URL + url).mock(
        return_value=httpx.Response(status_code=200, json=mock_json_response)
    )
    jobs = await init_linkedin.search_jobs(
        "Software Engineer",
        sort_by=SortBy.DATE,
        location=GeoID.USA,
        remote=[LocationType.ONSITE],
        limit=10,
    )
    assert jobs


@pytest.mark.asyncio
@respx.mock
async def test_search_jobs_v2(init_linkedin):
    mock_json_response = {
        "data": {
            "paging": {
                "total": 698,
                "start": 0,
                "count": 10,
                "links": [],
                "$recipeType": "com.linkedin.voyager.dash.deco.common.FullPaging",
            },
        },
        "elements": [
            {
                "$type": "com.linkedin.voyager.dash.jobs.JobPosting",
                "contentSource": "JOBS_PREMIUM_OFFLINE",
                "entityUrn": "urn:li:fsd_jobPosting:3967499755",
                "trackingUrn": "urn:li:jobPosting:3967499755",
                "$recipeType": "com.linkedin.deco.recipe.anonymous.Anon1578943416",
                "repostedJob": True,
                "title": "Python Developer",
                "posterId": "703343244",
            }
        ],
    }
    url = "/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-174&count=10&q=jobSearch&query=(origin:JOB_SEARCH_PAGE_QUERY_EXPANSION,selectedFilters:(workplaceType:List(1),sortBy:List(DD),timePostedRange:List(r86400)),spellCorrectionEnabled:true,keywords:Software+Engineer,locationUnion:(geoId:103644278))&start=0"
    respx.get(init_linkedin.client.API_BASE_URL + url).mock(
        return_value=httpx.Response(status_code=200, json=mock_json_response)
    )
    jobs = await init_linkedin.search_jobs(
        "Software Engineer",
        sort_by=SortBy.DATE,
        location=GeoID.USA,
        remote=[LocationType.ONSITE],
        limit=10,
        v2=True,
    )
    assert jobs


@pytest.mark.asyncio
@respx.mock
async def test_get_job(init_linkedin):
    job_id = "100"
    mock_json_response = {
        "jobPostingId": 100,
        "listedAt": 1720653929000,
        "title": "professional code monkey",
        "jobState": "LISTED",
        "description": {
            "text": "eating bananas",
        },
        "workRemoteAllowed": True,
        "formattedLocation": "Your mother's basement",
        "workplaceTypes": "1",
        "applyMethod": {
            "com.linkedin.voyager.jobs.ComplexOnsiteApply": {
                "unifyApplyEnabled": True,
                "easyApplyUrl": "https://www.linkedin.com/job-apply/3962991901",
            }
        },
    }
    respx.get(f"{init_linkedin.client.API_BASE_URL}/jobs/jobPostings/{job_id}").mock(
        return_value=httpx.Response(status_code=200, json=mock_json_response)
    )
    job_info = await init_linkedin.get_job(job_id)
    assert job_info


@pytest.mark.asyncio
@respx.mock
async def test_get_job_skills(init_linkedin):
    job_id = "3962991901"
    mock_json_response = {
        "companyUrn": "asasa",
        "entityUrn": "q23",
        "skillMatchStatuses": [
            {
                "localizedSkillDisplayName": "bananas",
                "skill": {"name": "naners"},
            }
        ],
    }
    respx.get(
        f"{init_linkedin.client.API_BASE_URL}/voyagerAssessmentsDashJobSkillMatchInsight/urn%3Ali%3Afsd_jobSkillMatchInsight%3A3962991901"
    ).mock(return_value=httpx.Response(status_code=200, json=mock_json_response))
    job_info = await init_linkedin.get_job_skills(job_id)
    assert job_info


@pytest.mark.asyncio
@respx.mock
async def test_search_companies(init_linkedin):
    mock_json_response = {
        "data": {
            "searchDashClustersByAll": {
                "_type": "com.linkedin.restli.common.CollectionResponse",
                "paging": {
                    "count": 10,
                    "start": 0,
                    "_type": "com.linkedin.restli.common.CollectionMetadata",
                    "total": 1000,
                    "_recipeType": "com.linkedin.81b214c2cdd4f02cdb7d827958d2f3a1",
                },
                "_recipeType": "com.linkedin.5f1d22f924ecb6a031ee124b8b767900",
                "elements": [
                    {
                        "image": None,
                        "quickFilterActions": [],
                        "clusterRenderType": "LIST",
                        "dismissable": False,
                        "totalResultCount": None,
                        "_type": "com.linkedin.voyager.dash.search.SearchClusterViewModel",
                        "controlName": None,
                        "description": None,
                        "_recipeType": "com.linkedin.5c853aba2154c55483e72bf6cdfaaf3e",
                        "title": None,
                        "actionTypeName": None,
                        "navigationText": None,
                        "feature": None,
                        "navigationCardAction": None,
                        "position": 1,
                        "items": [
                            {
                                "template": "UNIVERSAL",
                                "actorNavigationContext": None,
                                "trackingUrn": "urn:li:company:1441",
                                "controlName": None,
                                "interstitialComponent": None,
                                "primaryActions": [],
                                "entityCustomTrackingInfo": None,
                                "title": {
                                    "textDirection": "USER_LOCALE",
                                    "_type": "com.linkedin.voyager.dash.common.text.TextViewModel",
                                    "text": "Google",
                                    "attributesV2": [],
                                    "_recipeType": "com.linkedin.6a224ca38654a84754a1eb3e97c0f846",
                                    "accessibilityTextAttributesV2": [],
                                    "accessibilityText": None,
                                },
                                "overflowActions": [],
                                "searchActionType": None,
                                "actorInsights": [],
                                "insightsResolutionResults": [],
                                "badgeIcon": None,
                                "entityUrn": "urn:li:fsd_entityResultViewModel:(urn:li:fsd_company:1441,SEARCH_SRP,DEFAULT)",
                                "showAdditionalCluster": False,
                                "ringStatus": None,
                                "primarySubtitle": {
                                    "textDirection": "USER_LOCALE",
                                    "_type": "com.linkedin.voyager.dash.common.text.TextViewModel",
                                    "text": "Software Development • Mountain View, CA",
                                    "attributesV2": [],
                                    "_recipeType": "com.linkedin.6a224ca38654a84754a1eb3e97c0f846",
                                    "accessibilityTextAttributesV2": [],
                                    "accessibilityText": None,
                                },
                                "badgeText": None,
                                "trackingId": "sCoW5OaKRcWK5mUu6UIrkw==",
                                "addEntityToSearchHistory": True,
                                "actorNavigationUrl": None,
                                "summary": None,
                                "image": {
                                    "_type": "com.linkedin.voyager.dash.common.image.ImageViewModel",
                                    "attributes": [],
                                    "actionTarget": None,
                                    "_recipeType": "com.linkedin.fe5b8a3ac5a4a165c17f53b7eae4209b",
                                    "accessibilityTextAttributes": [],
                                    "totalCount": None,
                                    "accessibilityText": "Google",
                                },
                                "lazyLoadedActions": {
                                    "_recipeType": "com.linkedin.92ece182782ae4412e712925cd97f9fe",
                                    "_type": "com.linkedin.voyager.dash.search.LazyLoadedActions",
                                    "entityUrn": "urn:li:fsd_lazyLoadedActions:(urn:li:fsd_company:1441,COMPANIES,SEARCH_SRP)",
                                },
                                "secondarySubtitle": {
                                    "textDirection": "USER_LOCALE",
                                    "_type": "com.linkedin.voyager.dash.common.text.TextViewModel",
                                    "text": "33M followers",
                                    "attributesV2": [],
                                    "_recipeType": "com.linkedin.6a224ca38654a84754a1eb3e97c0f846",
                                    "accessibilityTextAttributesV2": [],
                                    "accessibilityText": None,
                                },
                                "_type": "com.linkedin.voyager.dash.search.EntityResultViewModel",
                                "navigationUrl": "https://www.linkedin.com/company/google/",
                                "entityEmbeddedObject": None,
                                "unreadIndicatorDetails": None,
                                "_recipeType": "com.linkedin.cf4b25c18907ea8eafe915c8bfa24109",
                                "target": None,
                                "actorTrackingUrn": None,
                                "navigationContext": {
                                    "_type": "com.linkedin.voyager.dash.search.NavigationContext",
                                    "openExternally": False,
                                    "_recipeType": "com.linkedin.55ee9afd4182671fe7e271f615659525",
                                    "url": "https://www.linkedin.com/company/google/",
                                },
                            }
                        ],
                        "results": [],
                    }
                ],
            }
        }
    }
    url = "/graphql?variables=(start:0,origin:GLOBAL_SEARCH_HEADER,query:(keywords:['google'],flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.b0928897b71bd00a5a7291755dcd64f0"
    respx.get(init_linkedin.client.API_BASE_URL + url).mock(
        return_value=httpx.Response(status_code=200, json=mock_json_response)
    )
    results = await init_linkedin.search_companies(keywords="google")
    assert results


@pytest.mark.asyncio
@respx.mock
async def test_get_profile_skills(init_linkedin):
    mock_json_response = {
        "paging": {"count": 100, "start": 0, "total": 10},
        "elements": [{"name": "picking my nose"}],
    }
    respx.get(
        init_linkedin.client.API_BASE_URL
        + f"/identity/profiles/{TEST_PROFILE_ID}/skills"
    ).mock(return_value=httpx.Response(status_code=200, json=mock_json_response))
    skills = await init_linkedin.get_profile_skills(TEST_PROFILE_ID)
    assert skills


@pytest.mark.asyncio
@respx.mock
async def test_get_updates(init_linkedin):
    mock_json_response = {
        "elements": [
            {
                "urn": "urn:li:activity:7196224250288955393",
                "entityUrn": "urn:li:fs_feedUpdate:(V2&COMPANY_FEED,urn:li:activity:7196224250288955393)",
                "id": "activity:7196224250288955393",
                "permalink": "https://www.linkedin.com/feed/update/urn:li:activity:7196224250288955393",
                "tracking": {
                    "requestId": "fde2539a-6b2c-40b3-b9ca-1d4b60e81062",
                    "trackingId": "vfn7hGmHhCFFNsPomNjUjg==",
                },
                "value": {
                    "com.linkedin.voyager.feed.render.UpdateV2": {
                        "commentary": {
                            "numLines": 3,
                            "text": {
                                "textDirection": "FIRST_STRONG",
                                "text": "Huge thanks to all the Googlers who made #GoogleIO possible this year and shared the innovations their teams have been working on. If you want to join us in building new tools in the Gemini era, find all our open roles in AI here: goo.gle/GoogleAIroles",
                            },
                        },
                        "socialDetail": {
                            "reactionElements": [],
                            "dashEntityUrn": "urn:li:fsd_socialDetail:(urn:li:ugcPost:7196223849250627584,urn:li:ugcPost:7196223849250627584,urn:li:highlightedReply:-)",
                            "comments": {
                                "paging": {"count": 100, "start": 0, "total": 10},
                                "elements": [],
                            },
                            "socialPermissions": {
                                "dashEntityUrn": "urn:li:fsd_socialPermissions:(urn:li:ugcPost:7196223849250627584,urn:li:fsd_profile:ACoAADYzqgYBoL6uqzyd69klOph8bMUEf7hYGTU)",
                                "canPostComments": True,
                                "entityUrn": "urn:li:fs_socialPermissions:(urn:li:ugcPost:7196223849250627584,urn:li:fs_profile:(ACoAADYzqgYBoL6uqzyd69klOph8bMUEf7hYGTU,en_US))",
                                "messagePermission": "PUBLIC",
                                "canShare": True,
                                "canReact": True,
                            },
                            "showPremiumAnalytics": False,
                            "hideFirstPrompt": True,
                            "liked": False,
                            "showShareButton": True,
                            "totalShares": 665,
                            "urn": "urn:li:ugcPost:7196223849250627584",
                            "threadId": "ugcPost:7196223849250627584",
                            "allowedCommentersScope": "ALL",
                            "totalSocialActivityCounts": {
                                "socialDetailEntityUrn": "urn:li:fs_socialDetail:urn:li:ugcPost:7196223849250627584",
                                "urn": "urn:li:ugcPost:7196223849250627584",
                                "numComments": 495,
                                "dashEntityUrn": "urn:li:fsd_socialActivityCounts:urn:li:ugcPost:7196223849250627584",
                                "reactionTypeCounts": [],
                                "entityUrn": "urn:li:fs_socialActivityCounts:urn:li:ugcPost:7196223849250627584",
                                "numShares": 665,
                                "numLikes": 7057,
                                "liked": False,
                            },
                            "entityUrn": "urn:li:fs_socialDetail:urn:li:ugcPost:7196223849250627584",
                            "commentingDisabled": False,
                            "likes": {
                                "paging": {"start": 0, "count": 100, "total": 10},
                                "elements": [],
                            },
                        },
                    }
                },
                "isSponsored": False,
            }
        ],
        "paging": {"count": 10, "start": 0, "links": []},
    }
    respx.get(init_linkedin.client.API_BASE_URL + "/feed/updates").mock(
        return_value=httpx.Response(status_code=200, json=mock_json_response)
    )
    posts = await init_linkedin.get_company_updates("gogole")
    assert posts


@pytest.mark.asyncio
@respx.mock
async def test_get_user_profile(init_linkedin):
    mock_json_response = {
        "plainId": 10000,
        "publicContactInfo": {},
        "premiumSubscriber": True,
        "miniProfile": {
            "firstName": "Sylvester",
            "lastName": "Stallone",
            "entityUrn": "helo wold",
            "publicIdentifier": "Rocky Balboa 46290",
        },
    }
    respx.get(init_linkedin.client.API_BASE_URL + "/me").mock(
        return_value=httpx.Response(status_code=200, json=mock_json_response)
    )
    me = await init_linkedin.get_user_profile()
    assert me
