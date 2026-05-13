import logging

from adapter.data_processing.template_parser import TemplateParser
from adapter.transport.sns_publisher import SnsPublisher as SnsPublisherLayer
from oidc_authn_context_listener.configuration import SnsPublishConfig, OIDC_AUTHN_USER_NOT_FOUND_KEY
from oidc_authn_context_listener.port.publisher import Publisher


class SnsPublisher(Publisher):

    def __init__(self, *, config: SnsPublishConfig, template_parser: TemplateParser):
        self.sns_publisher = SnsPublisherLayer(config=config.as_dict, template_parser=template_parser)

    def user_not_found(self, *, dto: dict):
        kwargs = self.sns_publisher.build_message_payload_with_str_data(
            data=dto,
            event_key=OIDC_AUTHN_USER_NOT_FOUND_KEY,
            entity_id=dto['userId'],
        )
        self._publish(dto=dto, message_payload_kwargs=kwargs)

    def _publish(self, *, dto: dict, message_payload_kwargs: dict):
        logging.debug(f'Message built: {message_payload_kwargs}')
        response = self.sns_publisher.publish_message(message_payload_kwargs=message_payload_kwargs)
        logging.info(f'Message published. MessageId: {response.get("MessageId")}, '
                     f'AccountId: {dto["accountId"]}, UserId: {dto["userId"]}.')
