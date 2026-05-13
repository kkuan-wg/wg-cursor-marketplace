import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from adapter.event.ddb_stream_event import DdbStreamEvent
from oidc_user_detail_listener.configuration import DdbStreamEventConfig
from tests.cache.oidc_user_detail_listener.ddb_stream_constants import USER_BLOCKED_EVENT, \
    USER_SOFT_DELETED_EVENT, USER_BLOCKED_DTO, USER_SOFT_DELETED_DTO


class TestDdbStream:
    @pytest.fixture
    def ddb_stream_event(self):
        return DdbStreamEvent(config=DdbStreamEventConfig().as_dict, template_parser=TemplateParser())

    @pytest.mark.parametrize('event, expected_dto', [
        param(USER_BLOCKED_EVENT, USER_BLOCKED_DTO, id='1'),
        param(USER_SOFT_DELETED_EVENT, USER_SOFT_DELETED_DTO, id='2')
    ])
    def test_parse_dto_with_success(self, event, expected_dto, ddb_stream_event):
        # Given

        # When
        actual_result = ddb_stream_event.as_dto(event=event)

        # Then
        assert actual_result == expected_dto
