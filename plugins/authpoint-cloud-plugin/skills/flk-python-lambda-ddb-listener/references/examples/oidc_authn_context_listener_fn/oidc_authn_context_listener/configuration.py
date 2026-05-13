from os import getenv

from configuration.base_config import BaseConfig
from flk_api.oidc.api_commons import TX_ENTITY_TYPE_OIDC_TRANSACTION, ApiEventType, TreatSyncNotificationEvent
from flk_api.oidc.api_config_helper import OidcApiRepositoryConfig

FUNCTION_NAME = 'flk-oidc-authn-context-listener'

AUTHN_CONTEXT_TYPE_GROUPING_MAP_KEY = 'authnContextTypeGroupingMapKey'

AUTHN_REQUESTED_MESSAGE_KEY = 'authnRequestedEntity'
AUTHZ_CODE_GENERATED_MESSAGE_KEY = 'authzCodeGeneratedEntity'
ID_TOKEN_GENERATED_MESSAGE_KEY = 'idTokenGeneratedEntity'
OIDC_AUTHN_USER_NOT_FOUND_KEY = 'oidcAuthnUserNotFound'

_SQS_CONFIG_AUTHN_REQUESTED_MESSAGE_DATA_KEY = 'authnRequestedMessageData'
_SQS_CONFIG_AUTHZ_CODE_GENERATED_MESSAGE_DATA_KEY = 'authzCodeGeneratedMessageData'
_SQS_CONFIG_ID_TOKEN_GENERATED_MESSAGE_DATA_KEY = 'idTokenGeneratedMessageData'
_SQS_CONFIG_MESSAGE_GROUP_ID_KEY = 'messageGroupId'
_SNS_CONFIG_MESSAGE_GROUP_ID_KEY = 'snsMessageGroupId'
_OIDC_AUTHENTICATION_FAILED = 'oidcAuthenticationFailed'

_BASE_SQS_DATA_MAPPING = {
    'accountId': 'accountId',
    'chainId': 'chainId',
    'userId': 'userId',
    'transactionId': 'transactionId',
    'header': 'header',
    'user': 'user'
}


class Environment:
    def __init__(self):
        self.aws_region = getenv('AWS_REGION')


class DdbStreamEventConfig(BaseConfig):
    def __init__(self):
        self.dto_mapping = {
            'accountId': 'newImage.accountId',
            'userId': 'newImage.userId',
            'transactionId': 'newImage.transactionId',
            'authnContextId': 'newImage.authnContextId',
            'chainId': 'newImage.chainId',
            'sessionId': 'newImage.sessionId',
            'contextType': 'newImage.contextType',
            'authnApiResult': 'newImage.authnApiResult',
            'userConfigResult': 'newImage.userConfigResult',
            'oidcAuthzCode': 'newImage.oidcAuthzCode',
            'oidcClient': 'newImage.oidcClient',
            'user': 'newImage.user',
            'city': 'newImage.city',
            'country': 'newImage.country',
        }
        self.dto_log_mapping = 'AccountId: {accountId}, ContextType: {contextType}'


class DdbRepositoryConfig(Environment, BaseConfig):
    def __init__(self):
        super().__init__()
        self.table_name = getenv('AUTHN_CONTEXT_TABLE_NAME')
        self.partition_key_schema = OidcApiRepositoryConfig.AUTHN_CONTEXT_REPOSITORY_AUTHN_CONTEXT_PK
        self.model_mappings = {
            AUTHN_CONTEXT_TYPE_GROUPING_MAP_KEY: OidcApiRepositoryConfig.AUTHN_CONTEXT_TYPE_GROUPING_MAP
        }


class SqsProducerConfig(BaseConfig, Environment):
    def __init__(self):
        super().__init__()
        self.queue_url = getenv('TX_REQUEST_QUEUE_URL')
        self.source = FUNCTION_NAME
        self.data_mappings = {
            _SQS_CONFIG_AUTHN_REQUESTED_MESSAGE_DATA_KEY: {
                'accountId': 'accountId',
                'chainId': 'chainId',
                'userId': 'userId',
                'transactionId': 'transactionId'
            },
            _SQS_CONFIG_AUTHZ_CODE_GENERATED_MESSAGE_DATA_KEY: _BASE_SQS_DATA_MAPPING,
            _SQS_CONFIG_ID_TOKEN_GENERATED_MESSAGE_DATA_KEY: _BASE_SQS_DATA_MAPPING,
        }
        self.message_group_id_schemas = {
            _SQS_CONFIG_MESSAGE_GROUP_ID_KEY: {
                'type': 'join',
                'value': {
                    'separator': '#',
                    'keys': ['accountId', {'type': 'hardcoded', 'value': 'TX'}, 'transactionId']
                }
            }
        }
        self.message_configs = {
            AUTHN_REQUESTED_MESSAGE_KEY: {
                'eventType': ApiEventType.OIDC_AUTHN_REQUESTED,
                'entityType': TX_ENTITY_TYPE_OIDC_TRANSACTION,
                'dataMappingKey': _SQS_CONFIG_AUTHN_REQUESTED_MESSAGE_DATA_KEY,
                'messageGroupIdSchemaKey': _SQS_CONFIG_MESSAGE_GROUP_ID_KEY,
            },
            AUTHZ_CODE_GENERATED_MESSAGE_KEY: {
                'eventType': ApiEventType.OIDC_AUTHZ_CODE_GENERATED,
                'entityType': TX_ENTITY_TYPE_OIDC_TRANSACTION,
                'dataMappingKey': _SQS_CONFIG_AUTHZ_CODE_GENERATED_MESSAGE_DATA_KEY,
                'messageGroupIdSchemaKey': _SQS_CONFIG_MESSAGE_GROUP_ID_KEY,
            },
            ID_TOKEN_GENERATED_MESSAGE_KEY: {
                'eventType': ApiEventType.OIDC_ID_TOKEN_GENERATED,
                'entityType': TX_ENTITY_TYPE_OIDC_TRANSACTION,
                'dataMappingKey': _SQS_CONFIG_ID_TOKEN_GENERATED_MESSAGE_DATA_KEY,
                'messageGroupIdSchemaKey': _SQS_CONFIG_MESSAGE_GROUP_ID_KEY,
            },
        }


class SnsPublishConfig(BaseConfig):
    def __init__(self):
        self.topic_arn = getenv('AUTHN_CONTEXT_TOPIC_ARN')
        self.source = FUNCTION_NAME
        self.aws_region = getenv('MAIN_REGION')
        self.event_data_mappings = {
            _OIDC_AUTHENTICATION_FAILED: {
                'accountId': 'accountId',
                'chainId': 'chainId',
                'city': 'city',
                'country': 'country',
                'userConfigResult': 'userConfigResult',
                'user': 'user',
                'oidcClient': 'oidcClient',
            }
        }
        self.message_group_id_schemas = {
            _SNS_CONFIG_MESSAGE_GROUP_ID_KEY: {
                'type': 'join',
                'value': {
                    'separator': '#',
                    'keys': ['accountId', {'type': 'hardcoded', 'value': 'USER'}, 'userId']
                }
            }
        }
        self.event_configs = {
            OIDC_AUTHN_USER_NOT_FOUND_KEY: {
                'eventType': TreatSyncNotificationEvent.OIDC_USER_NOT_FOUND_EVENT_TYPE,
                'entityType': TX_ENTITY_TYPE_OIDC_TRANSACTION,
                'dataMappingKey': _OIDC_AUTHENTICATION_FAILED,
                'messageGroupIdSchemaKey': _SNS_CONFIG_MESSAGE_GROUP_ID_KEY,
            },
        }
