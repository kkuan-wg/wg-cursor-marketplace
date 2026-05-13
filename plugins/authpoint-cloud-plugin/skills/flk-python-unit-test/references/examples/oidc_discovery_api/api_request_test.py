import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from adapter.event.http_event import HttpEvent
from oidc_discovery.configuration import HttpEventConfig
from tests.api.oidc_discovery.api_request_constants import EVENT, DTO, DTO_LOG


class TestApiRequest:

    @pytest.fixture
    def http_event(self):
        return HttpEvent(config=HttpEventConfig().as_dict, template_parser=TemplateParser())

    @pytest.mark.parametrize('actual_event, expected_result, expected_log', [
        param(EVENT, DTO, DTO_LOG, id='1')
    ])
    def test_parse_dto_with_success(self, actual_event, expected_result, expected_log, http_event):
        # Given

        # When
        actual_result = http_event.as_dto(event=actual_event)
        actual_log = str(actual_result)

        # Then
        assert actual_result == expected_result
        assert actual_log == expected_log
