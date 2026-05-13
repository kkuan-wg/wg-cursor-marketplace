from os import getenv

from configuration.base_config import BaseConfig
from flk_cache.cache_commons import AuthnCacheEntityType

FUNCTION_NAME = 'flk-core-data-cache-consumer'
DB_FORGOT_TOKEN_ENTITY = 'forgot_token_entity'
DB_PASSKEY_ENTITY = 'passkey_entity'
DB_USER_BLOCKLISTED_ENTITY = 'user_blocklisted_entity'

_BASE_CORE_ENTITY = {
    'accountId': 'accountId',
    'type': 'entityType',
    'externalId': 'entityId',
    'lastUpdatedOn': 'timestamp',
    'data': 'data'
}


class Environment:
    def __init__(self):
        self.aws_region = getenv('AWS_REGION')


class SqsEventConfig(BaseConfig):
    def __init__(self):
        self.dto_log_mapping = 'AccountId: {accountId}, EventType: {eventType}, EntityType: {entityType}, ' \
                               'EntityId: {entityId}'


class DdbForgotTokenRepositoryConfig(Environment, BaseConfig):
    def __init__(self):
        super().__init__()
        self.table_name = getenv('AUTHN_CACHE_TABLE_NAME')
        self.partition_key_schema = 'accountId'
        self.sort_key_schema = {
            'type': 'join',
            'value': {
                'separator': '#',
                'keys': [{'type': 'hardcoded', 'value': AuthnCacheEntityType.FORGOT_TOKEN}, 'entityId']
            }
        }
        self.model_mappings = {
            DB_FORGOT_TOKEN_ENTITY: _BASE_CORE_ENTITY
        }
        self.ttl_attribute_name = 'softDeletedTtl'
        self.ttl_delay_in_seconds = 86400


class DdbUserBlocklistedRepositoryConfig(Environment, BaseConfig):
    def __init__(self):
        super().__init__()
        self.table_name = getenv('AUTHN_CACHE_TABLE_NAME')
        self.partition_key_schema = 'accountId'
        self.sort_key_schema = {
            'type': 'join',
            'value': {
                'separator': '#',
                'keys': [{'type': 'hardcoded', 'value': AuthnCacheEntityType.USER_BLOCKLISTED}, 'entityId']
            }
        }
        self.model_mappings = {
            DB_USER_BLOCKLISTED_ENTITY: _BASE_CORE_ENTITY
        }


class DdbPasskeyRepositoryConfig(Environment, BaseConfig):
    def __init__(self):
        super().__init__()
        self.table_name = getenv('AUTHN_CACHE_TABLE_NAME')
        self.partition_key_schema = 'accountId'
        self.sort_key_schema = {
            'type': 'join',
            'value': {
                'separator': '#',
                'keys': [
                    {'type': 'hardcoded', 'value': AuthnCacheEntityType.PASSKEY},
                    'entityId',
                    {'type': 'hardcoded', 'value': 'CREDENTIAL_ID'},
                    'credentialId'
                ]
            }
        }
        self.model_mappings = {
            DB_PASSKEY_ENTITY: _BASE_CORE_ENTITY | {'externalId': 'credentialId'},
        }
        self.ttl_attribute_name = 'softDeletedTtl'
        self.ttl_delay_in_seconds = 86400
