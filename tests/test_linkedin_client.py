import httpx
import respx

from li_scrapi.client import LinkedInClient


@respx.mock
def test_authenticate():
    client = httpx.Client()
    linkedin_client = LinkedInClient(session=client)
    payload = {
        "session_key": "foo",
        "session_password": "bar",
        "JSESSIONID": "hello world",
    }
    respx.get(f"{linkedin_client.LINKEDIN_BASE_URL}/uas/authenticate").respond(
        status_code=200, cookies={"JSESSIONID": "hello world"}
    )
    respx.post(
        f"{linkedin_client.LINKEDIN_BASE_URL}/uas/authenticate",
        data=payload,
        headers=linkedin_client.AUTH_REQUEST_HEADERS,
        cookies=linkedin_client._session.cookies,
    ).mock(return_value=httpx.Response(status_code=200, json={"login_result": "PASS"}))
    respx.get(f"{linkedin_client.LINKEDIN_BASE_URL}")
    linkedin_client.authenticate("foo", "bar")
    client.close()
