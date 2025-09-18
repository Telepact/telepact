from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Client import Client
    from .Message import Message

class TestClient:
    def __init__(self, client: 'Client'):
        self.client = client

    async def assert_request(self, request_message: 'Message', expected_pseudo_json_body: dict[str, object], expect_match: bool) -> dict[str, object]:
        from .internal.mock.IsSubMap import is_sub_map

        result = await self.client.request(request_message)

        did_match = is_sub_map(expected_pseudo_json_body, result.body)

        if expect_match:
            if not did_match:
                raise AssertionError("Expected response body to match")
            return result.body
        else:
            if did_match:
                raise AssertionError("Expected response body to not match")
            return expected_pseudo_json_body