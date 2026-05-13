import logging
from copy import deepcopy
from datetime import timezone, datetime

import pytest
from pytest import param

from adapter.data_processing.template_parser import TemplateParser
from oidc_user_detail_listener.adapter.db_repository import DynamoDbRepository
from oidc_user_detail_listener.configuration import DdbRepositoryConfig
from oidc_user_detail_listener.domain.service import Service
from tests.cache.oidc_user_detail_listener.ddb_stream_constants import USER_BLOCKED_DTO, USER_SOFT_DELETED_DTO, \
    USER_IS_MFA_CHANGED_DTO, USER_WITH_NO_GROUP_CHANGES_AND_NO_TERMINATION_CONDITIONS_DTO, USER_GROUP_CHANGED_DTO
from tests.cache.oidc_user_detail_listener.service_constants import SINGLE_SESSION, MULTI_SESSIONS, \
    SESSION_01_TERMINATED_BY_USER_BLOCKED, MULTI_SESSIONS_TERMINATED_BY_USER_BLOCKED, \
    SESSION_01_TERMINATED_BY_SOFT_DELETE, SESSION_01_TERMINATED_BY_MFA_CHANGE, \
    SESSIONS_01_AND_03_TERMINATED_BY_MFA_CHANGE, MULTI_SESSIONS_SESSION_02_PREVIOUSLY_TERMINATED, \
    SESSION_01_UPDATE_GROUPS, SINGLE_SESSION_PREVIOUSLY_TERMINATED, MULTI_SESSIONS_PREVIOUSLY_TERMINATED

FAKE_NOW = datetime(2023, 12, 31, 0, 0, 0, 0, tzinfo=timezone.utc)


class TestService:

    @pytest.fixture
    def _patch_service_utcnow(self, mocker):
        patch_datetime = mocker.patch('oidc_user_detail_listener.domain.service.datetime')
        patch_datetime.now.return_value = FAKE_NOW

    @pytest.fixture
    def repository(self, mocker):
        mocker.patch('boto3.resource')
        return DynamoDbRepository(authn_context_config=DdbRepositoryConfig(), template_parser=TemplateParser())

    @pytest.fixture
    def service(self, repository, _patch_service_utcnow):
        return Service(repository=repository)

    @pytest.mark.parametrize('dto, db_sessions, expected_update_session_dtos', [
        param(USER_BLOCKED_DTO, SINGLE_SESSION, SESSION_01_TERMINATED_BY_USER_BLOCKED, id='1'),
        param(USER_SOFT_DELETED_DTO, SINGLE_SESSION, SESSION_01_TERMINATED_BY_SOFT_DELETE, id='2'),
        param(USER_IS_MFA_CHANGED_DTO, SINGLE_SESSION, SESSION_01_TERMINATED_BY_MFA_CHANGE, id='3'),
        param(USER_BLOCKED_DTO, MULTI_SESSIONS, MULTI_SESSIONS_TERMINATED_BY_USER_BLOCKED, id='4'),
        param(USER_IS_MFA_CHANGED_DTO, MULTI_SESSIONS_SESSION_02_PREVIOUSLY_TERMINATED,
              SESSIONS_01_AND_03_TERMINATED_BY_MFA_CHANGE, id='5'),
        param(USER_GROUP_CHANGED_DTO, SINGLE_SESSION, SESSION_01_UPDATE_GROUPS, id='6')
    ])
    def test_terminate_sessions_with_success(self, dto, db_sessions, expected_update_session_dtos, service, mocker):
        # Given
        service.repository.retrieve_sessions_by_account_id_and_user_id_including_soft_deleted = mocker.Mock(
            return_value=deepcopy(db_sessions)
        )
        service.repository.update_session = mocker.Mock()
        service.repository.update_groups = mocker.Mock()

        # When
        service.process(dto=dto)

        # Then
        service.repository.retrieve_sessions_by_account_id_and_user_id_including_soft_deleted.assert_called_once_with(
            dto=dto)
        service.repository.update_session.assert_has_calls(expected_update_session_dtos)
        service.repository.update_groups.assert_not_called()

    @pytest.mark.parametrize('dto, db_sessions', [
        param(USER_BLOCKED_DTO, {}, id='1'),
        param(USER_BLOCKED_DTO, [], id='2'),
        param(USER_BLOCKED_DTO, SINGLE_SESSION_PREVIOUSLY_TERMINATED, id='3'),
        param(USER_BLOCKED_DTO, MULTI_SESSIONS_PREVIOUSLY_TERMINATED, id='4'),
    ])
    def test_no_valid_sessions_found(self, dto, db_sessions, service, mocker):
        # Given
        service.repository.retrieve_sessions_by_account_id_and_user_id_including_soft_deleted = mocker.Mock(
            return_value=deepcopy(db_sessions)
        )
        service.repository.update_session = mocker.Mock()
        service.repository.update_groups = mocker.Mock()

        # When
        service.process(dto=dto)

        # Then
        service.repository.retrieve_sessions_by_account_id_and_user_id_including_soft_deleted.assert_called_once_with(
            dto=dto)
        service.repository.update_session.assert_not_called()
        service.repository.update_groups.assert_not_called()

    @pytest.mark.parametrize('dto', [
        param(USER_WITH_NO_GROUP_CHANGES_AND_NO_TERMINATION_CONDITIONS_DTO, id='1')
    ])
    def test_process_event_without_any_update(self, dto, service, caplog, mocker):
        # Given
        service.repository.retrieve_sessions_by_account_id_and_user_id_including_soft_deleted = mocker.Mock()
        service.repository.update_session = mocker.Mock()
        service.repository.update_groups = mocker.Mock()

        # When
        with caplog.at_level(logging.DEBUG):
            service.process(dto=dto)

        # Then
        assert 'User changes do not require session update.' in caplog.text
        service.repository.retrieve_sessions_by_account_id_and_user_id_including_soft_deleted.assert_not_called()
        service.repository.update_session.assert_not_called()
        service.repository.update_groups.assert_not_called()
