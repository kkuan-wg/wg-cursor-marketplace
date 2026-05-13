from adapter.data_processing.template_parser import TemplateParser
from adapter.datasource.ddb_repository import DdbRepository
from core_data_cache_consumer.configuration import DdbForgotTokenRepositoryConfig, DdbUserBlocklistedRepositoryConfig, \
    DdbPasskeyRepositoryConfig, DB_FORGOT_TOKEN_ENTITY, DB_USER_BLOCKLISTED_ENTITY, DB_PASSKEY_ENTITY
from core_data_cache_consumer.port.repository import Repository


class DynamoDbRepository(Repository):

    def __init__(self, *, forgot_token_config: DdbForgotTokenRepositoryConfig,
                 user_blocklisted_config: DdbUserBlocklistedRepositoryConfig,
                 passkey_config: DdbPasskeyRepositoryConfig, template_parser: TemplateParser):
        self.forgot_token_repository = DdbRepository(config=forgot_token_config.as_dict,
                                                     template_parser=template_parser)
        self.user_blocklisted_repository = DdbRepository(config=user_blocklisted_config.as_dict,
                                                         template_parser=template_parser)
        self.passkey_repository = DdbRepository(config=passkey_config.as_dict,
                                                template_parser=template_parser)

    def save_forgot_token(self, *, dto: dict):
        self.forgot_token_repository.save_item(dto=dto, model_mappings_entity_key=DB_FORGOT_TOKEN_ENTITY)

    def soft_delete_forgot_token(self, *, dto: dict):
        self.forgot_token_repository.soft_delete_item(dto=dto, model_mappings_entity_key=DB_FORGOT_TOKEN_ENTITY)

    def save_user_blocklisted(self, *, dto: dict):
        self.user_blocklisted_repository.save_item(dto=dto, model_mappings_entity_key=DB_USER_BLOCKLISTED_ENTITY)

    def save_passkey(self, *, dto: dict):
        self.passkey_repository.save_item(dto=dto, model_mappings_entity_key=DB_PASSKEY_ENTITY)
