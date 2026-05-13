import logging

from adapter.data_processing.template_parser import TemplateParser
from adapter.transport.sqs_producer import SqsProducer as SqsProducerLayer
from oidc_authn_context_listener.configuration import (
    SqsProducerConfig,
    AUTHN_REQUESTED_MESSAGE_KEY,
    AUTHZ_CODE_GENERATED_MESSAGE_KEY,
    ID_TOKEN_GENERATED_MESSAGE_KEY,
)
from oidc_authn_context_listener.port.producer import Producer


class SqsProducer(Producer):

    def __init__(self, *, config: SqsProducerConfig, template_parser: TemplateParser):
        self.sqs_producer = SqsProducerLayer(config=config.as_dict, template_parser=template_parser)

    def send_authn_requested(self, *, dto: dict):
        kwargs = self.sqs_producer.build_message_payload_with_obj_data(
            data=dto, message_key=AUTHN_REQUESTED_MESSAGE_KEY
        )
        self._send(dto=dto, message_payload_kwargs=kwargs)

    def send_authz_code_generated(self, *, dto: dict):
        kwargs = self.sqs_producer.build_message_payload_with_obj_data(
            data=dto, message_key=AUTHZ_CODE_GENERATED_MESSAGE_KEY
        )
        self._send(dto=dto, message_payload_kwargs=kwargs)

    def send_id_token_generated(self, *, dto: dict):
        kwargs = self.sqs_producer.build_message_payload_with_obj_data(
            data=dto, message_key=ID_TOKEN_GENERATED_MESSAGE_KEY
        )
        self._send(dto=dto, message_payload_kwargs=kwargs)

    def _send(self, *, dto: dict, message_payload_kwargs: dict):
        logging.debug(f'Message built: {message_payload_kwargs}')
        response = self.sqs_producer.send_message(message_payload_kwargs=message_payload_kwargs)
        logging.info(f'Message sent. MessageId: {response.get("MessageId")}, '
                     f'AccountId: {dto.get("accountId")}, ContextType: {dto.get("contextType")}.')
