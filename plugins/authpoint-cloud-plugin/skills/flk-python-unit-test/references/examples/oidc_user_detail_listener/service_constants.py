from unittest.mock import call

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

SESSION_01 = {
    'partitionKey': 'WGC-123456789#SESSION#57abff02-9434-494c-ad30-4c4542f1a98a',
    'sortKey': 'TRANSACTION#abc-123-xyz-456',
    'authnContextGsi': 'USER#123',
    'sortKeyGsi': 'WGC-123456789#SESSION#57abff02-9434-494c-ad30-4c4542f1a98a',
    'accountId': 'WGC-123456789',
    'userId': 123,
    'sessionId': '57abff02-9434-494c-ad30-4c4542f1a98a',
    'transactionId': 'abc-123-xyz-456',
    'softDeletedTtl': 1694678400000,
    'expirationTimeInMillis': 1703980800333,
    'creationTimeInMillis': 1694649600000,
    'header': _HEADER,
    'user': _USER
}

SESSION_02 = {
    'partitionKey': 'WGC-123456789#SESSION#7af293ea-4f2c-445d-9327-40d79de9c1c9',
    'sortKey': 'TRANSACTION#abc-123-xyz-456',
    'authnContextGsi': 'USER#123',
    'sortKeyGsi': 'WGC-123456789#SESSION#7af293ea-4f2c-445d-9327-40d79de9c1c9',
    'accountId': 'WGC-123456789',
    'userId': 123,
    'sessionId': '7af293ea-4f2c-445d-9327-40d79de9c1c9',
    'transactionId': 'abc-123-xyz-456',
    'softDeletedTtl': 1694678400000,
    'expirationTimeInMillis': 1703980800666,
    'creationTimeInMillis': 1694649600000,
    'header': _HEADER,
    'user': _USER
}

SESSION_03 = {
    'partitionKey': 'WGC-123456789#SESSION#0e36259d-2b38-42a9-b731-08cd107b25b1',
    'sortKey': 'TRANSACTION#abc-123-xyz-456',
    'authnContextGsi': 'USER#123',
    'sortKeyGsi': 'WGC-123456789#SESSION#0e36259d-2b38-42a9-b731-08cd107b25b1',
    'accountId': 'WGC-123456789',
    'userId': 123,
    'sessionId': '0e36259d-2b38-42a9-b731-08cd107b25b1',
    'transactionId': 'abc-123-xyz-456',
    'softDeletedTtl': 1694678400000,
    'expirationTimeInMillis': 1703980800999,
    'creationTimeInMillis': 1694649600000,
    'header': _HEADER,
    'user': _USER
}

_PAST_EXPIRATION_TIME = 1703980800000

SINGLE_SESSION = [SESSION_01]

MULTI_SESSIONS = [SESSION_01, SESSION_02, SESSION_03]

SINGLE_SESSION_PREVIOUSLY_TERMINATED = [SESSION_01 | {'expirationTimeInMillis': _PAST_EXPIRATION_TIME}]

MULTI_SESSIONS_SESSION_02_PREVIOUSLY_TERMINATED = [
    SESSION_01,
    SESSION_02 | {'expirationTimeInMillis': _PAST_EXPIRATION_TIME},
    SESSION_03]

MULTI_SESSIONS_PREVIOUSLY_TERMINATED = [
    SESSION_01 | {'expirationTimeInMillis': _PAST_EXPIRATION_TIME},
    SESSION_02 | {'expirationTimeInMillis': _PAST_EXPIRATION_TIME},
    SESSION_03 | {'expirationTimeInMillis': _PAST_EXPIRATION_TIME}
]

# EXPECTED DTO UPDATES

SESSION_01_TERMINATED_BY_USER_BLOCKED = [
    call(**{
        'dto': {
            **SESSION_01,
            'expirationTimeInMillis': _PAST_EXPIRATION_TIME,
            'user': {
                **SESSION_01.get('user'),
                'status': 'BLOCKED',
                'overAllocated': False,
                'quarantine': False,
                'isMfa': True
            }
        }
    })
]

SESSION_01_TERMINATED_BY_SOFT_DELETE = [
    call(**{
        'dto': {
            **SESSION_01,
            'expirationTimeInMillis': _PAST_EXPIRATION_TIME,
            'user': {
                **SESSION_01.get('user'),
                'status': 'BLOCKED',
                'overAllocated': False,
                'quarantine': False,
                'isMfa': False
            }
        }
    })
]

SESSION_01_TERMINATED_BY_MFA_CHANGE = [
    call(**{
        'dto': {
            **SESSION_01,
            'expirationTimeInMillis': _PAST_EXPIRATION_TIME,
            'user': {
                **SESSION_01.get('user'),
                'status': 'ACTIVE',
                'overAllocated': False,
                'quarantine': False,
                'isMfa': True
            }
        }
    })
]

MULTI_SESSIONS_TERMINATED_BY_USER_BLOCKED = [
    call(**{
        'dto': {
            **SESSION_01,
            'expirationTimeInMillis': _PAST_EXPIRATION_TIME,
            'user': {
                **SESSION_01.get('user'),
                'status': 'BLOCKED',
                'overAllocated': False,
                'quarantine': False,
                'isMfa': True
            }
        }
    }),
    call(**{
        'dto': {
            **SESSION_02,
            'expirationTimeInMillis': _PAST_EXPIRATION_TIME,
            'user': {
                **SESSION_02.get('user'),
                'status': 'BLOCKED',
                'overAllocated': False,
                'quarantine': False,
                'isMfa': True
            }
        }
    }),
    call(**{
        'dto': {
            **SESSION_03,
            'expirationTimeInMillis': _PAST_EXPIRATION_TIME,
            'user': {
                **SESSION_03.get('user'),
                'status': 'BLOCKED',
                'overAllocated': False,
                'quarantine': False,
                'isMfa': True
            }
        }
    }),
]

SESSIONS_01_AND_03_TERMINATED_BY_MFA_CHANGE = [
    call(**{
        'dto': {
            **SESSION_01,
            'expirationTimeInMillis': _PAST_EXPIRATION_TIME,
            'user': {
                **SESSION_01.get('user'),
                'status': 'ACTIVE',
                'overAllocated': False,
                'quarantine': False,
                'isMfa': True
            }
        }
    }),
    call(**{
        'dto': {
            **SESSION_03,
            'expirationTimeInMillis': _PAST_EXPIRATION_TIME,
            'user': {
                **SESSION_03.get('user'),
                'status': 'ACTIVE',
                'overAllocated': False,
                'quarantine': False,
                'isMfa': True
            }
        }
    })
]

SESSION_01_UPDATE_GROUPS = [
    call(**{
        'dto': {
            **SESSION_01,
            'expirationTimeInMillis': _PAST_EXPIRATION_TIME,
            'user': {
                **SESSION_01.get('user')
            }
        }
    })
]
