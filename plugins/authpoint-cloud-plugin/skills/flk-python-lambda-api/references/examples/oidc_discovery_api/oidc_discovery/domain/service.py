import logging
from copy import deepcopy

from utils.validation_helper import ValidationException, DtoValidator
from oidc_discovery.port.repository import ClientConfigRepositoryPort
from oidc_discovery.port.responder import ResponderPort

RESPONSE_TYPES_MAX_COUNT = 2  # max count of different response types an account can have


class Service:
    def __init__(self, client_config_repository: ClientConfigRepositoryPort, responder: ResponderPort):
        self.client_config_repository = client_config_repository
        self.responder = responder
        self.event_validator = EventValidator()

    def process(self, *, dto: dict) -> dict:
        logging.info(f'Processing DTO. {dto}')
        try:
            self.event_validator.validate_request(dto=dto)
            clients = self.client_config_repository.retrieve_oidc_clients_by_account_id(dto=dto)
            self._validate_clients(clients=clients)
            issuer = self._get_issuer(clients=clients)
            response_types = self._get_account_response_types(clients=clients)
            response_dto = self._build_response_dto(dto=dto, issuer=issuer, response_types=response_types)
            return self.responder.success(dto=response_dto)
        except ValidationException as ex:
            logging.error(ex)
            return self.responder.invalid_request(param=ex.param, dto=dto)

    def _build_response_dto(self, *, dto: dict, issuer: str, response_types: list) -> dict:
        response_dto = deepcopy(dto)
        response_dto['openIdConfiguration'] = self._build_openid_configuration(issuer=issuer,
                                                                               response_types=response_types)
        return response_dto

    @staticmethod
    def _validate_clients(*, clients: list):
        if not clients:
            raise ValidationException(param='clients')

    @staticmethod
    def _get_issuer(*, clients: list) -> str:
        return next(client.get('issuer') for client in clients)

    @staticmethod
    def _get_account_response_types(*, clients: list) -> list:
        response_types = set()
        for client in clients:
            response_types.add('id_token' if client.get('responseType') == 'id_token' else 'code')
            if len(response_types) == RESPONSE_TYPES_MAX_COUNT:
                break
        return sorted(response_types)

    @staticmethod
    def _build_openid_configuration(*, issuer: str, response_types: list) -> dict:
        open_id_configuration = {
            'issuer': issuer,
            'authorization_endpoint': f'{issuer}/authorize',
            'jwks_uri': f'{issuer}/cert',
            'userinfo_endpoint': f'{issuer}/userinfo',
            'scopes_supported': ['openid', 'email', 'profile'],
            'response_types_supported': response_types,
            'subject_types_supported': ['public'],
            'id_token_signing_alg_values_supported': ['RS256'],
            'claim_types_supported': ['normal']
        }
        if 'code' in response_types:
            open_id_configuration.update({
                'token_endpoint': f'{issuer}/token',
                'token_endpoint_auth_methods_supported': ['client_secret_basic']
            })
        return open_id_configuration


class EventValidator:
    REQUIRED_FIELDS = {'accountId': {'type': str, 'minLength': 5}}

    def __init__(self):
        self.dto_validator = DtoValidator()

    def validate_request(self, *, dto: dict):
        self._validate_required_fields(dto=dto)

    def _validate_required_fields(self, *, dto: dict):
        self.dto_validator.validate_required_fields(dto=dto, required_fields=EventValidator.REQUIRED_FIELDS)
