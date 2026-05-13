import logging

from core_data_cache_consumer.port.repository import Repository
from flk_core.core_commons import CoreCredentialEntityType, CoreTxEntityType, CoreCredentialDataEventType, \
    CoreTransactionEventType
from utils.validation_helper import DtoValidator, ValidationException


class Service:

    def __init__(self, *, repository: Repository):
        self.repository = repository
        self.event_validator = EventValidator()

    def process(self, *, dto: dict):
        logging.info(f'Processing DTO {dto}')

        try:
            self.event_validator.validate_required_fields(dto=dto)
            if dto['entityType'] == CoreCredentialEntityType.CREDENTIAL_TYPE_FORGOT_TOKEN:
                self._handle_forgot_token(dto=dto)
            elif dto['entityType'] == CoreTxEntityType.USER_BLOCKLISTED:
                self.repository.save_user_blocklisted(dto=dto)
                logging.debug(f'Message processed. {dto}')
            elif dto['entityType'] == CoreCredentialEntityType.CREDENTIAL_TYPE_PASSKEY:
                self.event_validator.validate_passkey_data(dto=dto)
                dto['credentialId'] = dto['data']['credentialId']
                self.repository.save_passkey(dto=dto)
                logging.debug(f'Message processed. {dto}')
            else:
                logging.error(f'Message discarded. Invalid entityType. {dto}.')
        except ValidationException as ex:
            logging.error(f'Message discarded: {dto}. Exception: {ex}.')

    def _handle_forgot_token(self, dto: dict):
        if dto['eventType'] in [CoreCredentialDataEventType.CORE_FORGOT_TOKEN_REQUESTED,
                                CoreCredentialDataEventType.CORE_FORGOT_TOKEN_ACTIVATED]:
            self.repository.save_forgot_token(dto=dto)
        else:
            self.repository.soft_delete_forgot_token(dto=dto)
        logging.debug(f'Message processed. {dto}')


class EventValidator:
    VALID_EVENT_TYPES = [CoreCredentialDataEventType.CORE_FORGOT_TOKEN_REQUESTED,
                         CoreCredentialDataEventType.CORE_FORGOT_TOKEN_ACTIVATED,
                         CoreCredentialDataEventType.CORE_FORGOT_TOKEN_DEACTIVATED,
                         CoreTransactionEventType.EVENT_TYPE_AZURE_AD_USER_ACCOUNT_LOCKED,
                         CoreCredentialDataEventType.CORE_PASSKEY_ADDED]

    REQUIRED_FIELDS = {
        'accountId': str,
        'entityId': str
    }

    PASSKEY_DATA_REQUIRED_FIELDS = {
        'credentialId': str
    }

    def __init__(self):
        self.dto_validator = DtoValidator()

    def validate_required_fields(self, *, dto: dict):
        self._validate_event_type(dto=dto)
        self._validate_event_data(dto=dto)

    def validate_passkey_data(self, *, dto: dict):
        self.dto_validator.validate_required_fields(dto=dto.get('data', {}),
                                                    required_fields=self.PASSKEY_DATA_REQUIRED_FIELDS)

    def _validate_event_data(self, *, dto: dict):
        self.dto_validator.validate_required_fields(dto=dto, required_fields=self.REQUIRED_FIELDS)

    def _validate_event_type(self, *, dto: dict):
        if dto.get('eventType') not in self.VALID_EVENT_TYPES:
            raise ValidationException(param='eventType')
