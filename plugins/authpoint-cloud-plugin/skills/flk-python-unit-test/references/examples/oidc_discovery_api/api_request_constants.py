ACCOUNT_ID = 'WGC-0'
REQUEST_ID = '123'

# EVENTS
EVENT = {
    'resource': 'abc',
    'httpMethod': 'GET',
    'stageVariables': 'None',
    'headers': {
        'Request-Id': REQUEST_ID,
    },
    'requestContext': {
        'extendedRequestId': REQUEST_ID,
        'identity': {
            'sourceIp': '1.1.1.1'
        }
    },
    'pathParameters': {
        'accountId': ACCOUNT_ID
    }
}

DTO = {
    'accountId': ACCOUNT_ID,
    'extendedRequestId': REQUEST_ID,
    'httpMethod': 'GET',
    'pathParamAccountId': 'WGC-0',
    'resourceEndpoint': 'abc',
    'requestId': REQUEST_ID
}

DTO_LOG = 'AccountId: WGC-0, ExtendedRequestId: 123, RequestId: 123, HttpMethod: GET'
