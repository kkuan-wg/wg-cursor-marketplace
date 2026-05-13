import logging

from authn_cache_stream_listener.port.publisher import Publisher


class Service:

    def __init__(self, *, publisher: Publisher):
        self.sns_publisher = publisher

    def process(self, *, dto: dict):
        logging.info(f'Processing DTO {dto}')

        if dto.get('eventType') == 'INSERT':
            self.sns_publisher.add_cache_item(dto=dto)
        elif dto.get('eventType') == 'MODIFY':
            if dto.get('softDeletedTtl', 0) > 0:
                self.sns_publisher.delete_cache_item(dto=dto)
            else:
                self.sns_publisher.update_cache_item(dto=dto)
        else:
            logging.error(f'Message discarded. Invalid event. {dto}')
