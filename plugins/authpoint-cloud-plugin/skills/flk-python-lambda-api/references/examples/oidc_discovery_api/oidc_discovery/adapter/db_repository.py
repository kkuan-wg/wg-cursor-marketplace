from adapter.data_processing.template_parser import TemplateParser
from adapter.datasource.ddb_repository import DdbRepository
from oidc_discovery.configuration import ClientConfigDdbRepositoryConfig, DB_OIDC_CLIENT_CONFIG_GSI_NAME
from oidc_discovery.port.repository import ClientConfigRepositoryPort


class ClientConfigRepository(ClientConfigRepositoryPort):
    def __init__(self, *, config: ClientConfigDdbRepositoryConfig, template_parser: TemplateParser):
        self.client_config_repository = DdbRepository(config=config.as_dict, template_parser=template_parser)

    def retrieve_oidc_clients_by_account_id(self, *, dto: dict) -> list:
        return self.client_config_repository.query_gsi_by_partition_key(dto=dto,
                                                                        index_name=DB_OIDC_CLIENT_CONFIG_GSI_NAME)
