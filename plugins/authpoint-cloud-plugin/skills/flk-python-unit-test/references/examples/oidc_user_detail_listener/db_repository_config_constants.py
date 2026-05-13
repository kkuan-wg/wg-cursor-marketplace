AUTHN_CONTEXT_GSI_NAME = 'flk-oidc-authn-context-authn-context-gsi'

GSI_KEY = 'WGC-123456789#USER#123'

PARTITION_KEY = 'WGC-123456789#SESSION#57abff02-9434-494c-ad30-4c4542f1a98a'

SORT_KEY = 'TRANSACTION#abc-123-xyz-456'

_HEADER = {
    'accountId': 'WGC-123456789',
    'transactionId': 'abc-123-xyz-456',
    'resourceId': 1,
    'resourceName': 'my firewan',
    'resourceType': 'OIDC',
    'friendlyType': 'WG_INTERNAL',
    'applicationType': 'FIREWAN',
    'clientId': '123-abc',
    'issuer': 'issuer',
    'clientIp': '1.0.0.1',
    'redirectUri': 'http://localhost:4200/callback',
    'state': '1599045135410-jFe',
    'nonce': '1599046102647-dv4',
    'accuracy': 11.71,
    'latitude': -33.0,
    'longitude': 44.0,
    'lastUpdatedOn': 121234800300
}

_USER = {
    'userId': 123,
    'status': 'ACTIVE',
    'quarantine': False,
    'overAllocated': False,
    'groups': [71, 72, 73],
    'firstName': 'luffy',
    'lastName': 'monkey d.',
    'username': 'luffy',
    'email': 'luffy@email.com',
    'loginType': 'EMAIL',
    'authnTypes': ['password'],
    'userType': 'AUTH_POINT',
    'isMfa': False,
}

SESSION = {
    'partitionKey': 'WGC-123456789#SESSION#57abff02-9434-494c-ad30-4c4542f1a98a',
    'sortKey': 'TRANSACTION#abc-123-xyz-456',
    'authnContextGsi': 'USER#123',
    'sortKeyGsi': 'WGC-123456789#SESSION#57abff02-9434-494c-ad30-4c4542f1a98a',
    'accountId': 'WGC-123456789',
    'userId': 123,
    'sessionId': '57abff02-9434-494c-ad30-4c4542f1a98a',
    'transactionId': 'abc-123-xyz-456',
    'softDeletedTtl': 1694678400000,
    'expirationTimeInMillis': 1694678400000,
    'creationTimeInMillis': 1694649600000,
    'header': _HEADER,
    'user': _USER
}

SESSION_EXPIRED = SESSION | {'expirationTimeInMillis': 1694678300666}

UPDATE_EXPIRATION_TIME_SESSION_MODEL = {
    'expirationTimeInMillis': 1694678300666,
    'user': _USER
}
