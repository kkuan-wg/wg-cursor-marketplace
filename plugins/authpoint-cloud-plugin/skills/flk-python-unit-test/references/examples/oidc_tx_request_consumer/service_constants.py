from tests.transaction.consumer.oidc_tx_request_consumer.sqs_message_constants import (
    AUTHN_REQUESTED_DTO, TRANSACTION_TIMEOUT_DTO, AUTHZ_CODE_GENERATED_DTO, ID_TOKEN_GENERATED_DTO)

FAKE_NOW_IN_MILLIS = 1690761600000

# REQUIRED FIELDS VALIDATION DTOs

EVENT_REQUIRED_FIELDS = {
    'accountId': str,
    'transactionId': str,
    'userId': int
}

INVALID_ENTITY_TYPE_DTO = {
    'eventType': 'OIDC_TRANSACTION_CREATED',
    'entityType': 'LDAP',
    'accountId': 'WGC-0',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'messageId': 'ca9bc51b-ba57-4a78-a337-b26e414085e5',
    'source': 'flk-ldap-authn-api',
    'timestamp': 12334567,
}

INVALID_EVENT_TYPE_DTO = {
    'eventType': 'TRANSACTION',
    'entityType': 'OIDC_TRANSACTION',
    'accountId': 'WGC-0',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'messageId': 'ca9bc51b-ba57-4a78-a337-b26e414085e5',
    'source': 'flk-oidc-authn-api',
    'timestamp': 12334567,
}

MISSING_ACCOUNT_ID_DTO = {
    'eventType': 'OIDC_TRANSACTION_CREATED',
    'entityType': 'OIDC_TRANSACTION',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'messageId': 'ca9bc51b-ba57-4a78-a337-b26e414085e5',
    'source': 'flk-oidc-authn-api',
    'timestamp': 12334567,
}

MISSING_TRANSACTION_ID_DTO = {
    'eventType': 'OIDC_TRANSACTION_CREATED',
    'entityType': 'OIDC_TRANSACTION',
    'accountId': 'WGC-0',
    'userId': 12,
    'messageId': 'ca9bc51b-ba57-4a78-a337-b26e414085e5',
    'source': 'flk-oidc-authn-api',
    'timestamp': 12334567,
}

# AUTHN_REQUESTED DTOs

AUTHN_REQUESTED_WITH_USER_ERROR_DTO = {
    'eventType': 'OIDC_AUTHN_REQUESTED',
    'entityType': 'OIDC_TRANSACTION',
    'accountId': 'WGC-0',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'messageId': 'ca9bc51b-ba57-4a78-a337-b26e414085e5',
    'source': 'flk-oidc-authn-api',
    'timestamp': 12334567,
    'header': {
        'accountId': 'WGC-0',
        'applicationType': 'FIREWAN',
        'clientId': '123-abc',
        'clientIp': '1.0.0.1',
        'clientSecret': 'client_secret',
        'friendlyType': 'WG_INTERNAL',
        'nonce': '1599046102647-dv4',
        'redirectUri': 'http://localhost:4200/callback',
        'resourceId': 1,
        'resourceName': 'my firewan',
        'resourceType': 'OIDC',
        'state': '1599045135410-jFe',
        'transactionId': 'abc-123-xyz-456'
    },
    'user': {
        'authnTypes': ['password', 'push'],
        'isMfa': False,
        'userId': 12,
        'userType': 'AUTH_POINT'
    }
}

AUTHN_REQUESTED_WITH_HEADER_ERROR_DTO = {
    'eventType': 'OIDC_AUTHN_REQUESTED',
    'entityType': 'OIDC_TRANSACTION',
    'accountId': 'WGC-0',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'messageId': 'ca9bc51b-ba57-4a78-a337-b26e414085e5',
    'source': 'flk-oidc-authn-api',
    'timestamp': 12334567,
    'header': {
        'accountId': 'WGC-0',
        'applicationType': 'FIREWAN',
        'clientIp': '1.0.0.1',
        'clientSecret': 'client_secret',
        'friendlyType': 'WG_INTERNAL',
        'redirectUri': 'http://localhost:4200/callback',
        'resourceId': 1,
        'resourceName': 'my firewan',
        'resourceType': 'OIDC',
        'state': '1599045135410-jFe',
        'transactionId': 'abc-123-xyz-456'
    },
    'user': {
        'authnTypes': ['password'],
        'email': 'luffy@email.com',
        'firstName': 'luffy',
        'isMfa': False,
        'lastName': 'monkey d.',
        'loginType': 'USERNAME',
        'userId': 12,
        'userType': 'AUTH_POINT',
        'username': 'luffy'
    }
}

# CORE AUTHENTICATION TRANSACTION DTOs

PASSWORD_VALIDATED_MISSING_AUTHN_RESULT_FIELD_DTO = {
    'eventType': 'PASSWORD_VALIDATED',
    'accountId': 'WGC-0',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'entityType': 'OIDC_AUTHENTICATION',
    'messageId': '9a214fef-594f-4bbc-bee1-eaa9b9703fa1',
    'source': 'flk-authn-core-local-password-api',
    'timestamp': 123456789,
    'authnResult': {
        'authnTypes': ['password'],
        'authnFailureReason': None,
        'authnTimestamp': 123456789
    }
}
PASSWORD_VALIDATED_INVALID_EVENT_TYPE_FIELD_DTO = {
    'eventType': 'ASSWORD_VALIDATED',
    'accountId': 'WGC-0',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'entityType': 'OIDC_AUTHENTICATION',
    'messageId': '9a214fef-594f-4bbc-bee1-eaa9b9703fa1',
    'source': 'flk-authn-core-local-password-api',
    'timestamp': 123456789,
    'authnResult': {
        'authnTypes': ['password'],
        'authnFailureReason': None,
        'authnTimestamp': 123456789
    }
}

PASSWORD_VALIDATED_INVALID_AUTHN_TYPES_FIELD_DTO = {
    'eventType': 'PASSWORD_VALIDATED',
    'accountId': 'WGC-0',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'entityType': 'OIDC_AUTHENTICATION',
    'messageId': '9a214fef-594f-4bbc-bee1-eaa9b9703fa1',
    'source': 'flk-authn-core-local-password-api',
    'timestamp': 123456789,
    'authnResult': {
        'authnTypes': ['password', 'invalid'],
        'authnFailureReason': None,
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 123456789
    }
}

# DDB ITEMS

_BASE_HEADER = {
    'accountId': 'WGC-123-abc',
    'applicationType': 'FIREWAN',
    'clientId': '123-abc',
    'clientIp': '1.0.0.1',
    'clientSecret': 'client_secret',
    'friendlyType': 'WG_INTERNAL',
    'lastUpdatedOn': 12334567,
    'nonce': '1599046102647-dv4',
    'redirectUri': 'http://localhost:4200/callback',
    'resourceId': 1,
    'resourceName': 'my firewan',
    'resourceType': 'OIDC',
    'state': '1599045135410-jFe',
    'transactionId': 'abc-123-xyz-456',
}

_BASE_USER = {
    'accountId': 'WGC-123-abc',
    'authnTypes': ['password'],
    'email': 'luffy@email.com',
    'firstName': 'luffy',
    'isMfa': False,
    'lastName': 'monkey d.',
    'lastUpdatedOn': 12334567,
    'loginType': 'USERNAME',
    'userId': 12,
    'userType': 'AUTH_POINT',
    'username': 'luffy'
}

DB_TRANSACTION_PW_PROCESSING = {
    'partitionKey': 'WGC-123-abc',
    'sortKey': 'TRANSACTION#abc-123-xyz-456',
    'transactionResult': {
        'transactionStatus': 'PROCESSING',
        'lastUpdatedOn': 12334567
    },
    'softDeletedTtl': 1632961500,
    'header': {
        **_BASE_HEADER,
        'latitude': -33.8978,
        'longitude': 151.1899
    },
    'user': _BASE_USER
}

DB_TRANSACTION_PW_PROCESSING_WITHOUT_VALID_GEOLOCATION = {
    'partitionKey': 'WGC-123-abc',
    'sortKey': 'TRANSACTION#abc-123-xyz-456',
    'transactionResult': {
        'transactionStatus': 'PROCESSING',
        'lastUpdatedOn': 12334567
    },
    'softDeletedTtl': 1632961500,
    'header': _BASE_HEADER,
    'user': _BASE_USER
}

DB_TRANSACTION_PW_OTP_PROCESSING = {
    'partitionKey': 'WGC-123-abc',
    'sortKey': 'TRANSACTION#abc-123-xyz-456',
    'transactionResult': {
        'transactionStatus': 'PROCESSING',
        'lastUpdatedOn': 12334567
    },
    'softDeletedTtl': 1632961500,
    'header': {**_BASE_HEADER, 'latitude': -33.8978, 'longitude': 151.1899},
    'user': {**_BASE_USER, 'authnTypes': ['password', 'otp']}
}

DB_TRANSACTION_PASSKEY_PROCESSING = {
    'partitionKey': 'WGC-123-abc',
    'sortKey': 'TRANSACTION#abc-123-xyz-456',
    'transactionResult': {
        'transactionStatus': 'PROCESSING',
        'lastUpdatedOn': 12334567
    },
    'softDeletedTtl': 1632961500,
    'header': {**_BASE_HEADER, 'latitude': -33.8978, 'longitude': 151.1899},
    'user': {**_BASE_USER, 'authnTypes': ['passkey'], 'isMfa': True}
}

DB_TRANSACTION_DONE_WITHOUT_VALID_GEOLOCATION = {
    'partitionKey': 'WGC-123-abc',
    'sortKey': 'TRANSACTION#abc-123-xyz-456',
    'transactionResult': {
        'transactionStatus': 'AUTHN_DONE',
        'authnFailureReason': None,
        'authnFailureReasonCode': None,
        'authnFailureReasonMessage': None,
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 1690761600
    },
    'softDeletedTtl': 1632961500,
    'header': {
        **_BASE_HEADER
    },
    'user': _BASE_USER
}

DB_TRANSACTION_DONE = {
    'partitionKey': 'WGC-123-abc',
    'sortKey': 'TRANSACTION#abc-123-xyz-456',
    'transactionResult': {
        'transactionStatus': 'AUTHN_DONE',
        'authnFailureReason': None,
        'authnFailureReasonCode': None,
        'authnFailureReasonMessage': None,
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 1690761600,
    },
    'softDeletedTtl': 1632961500,
    'header': {
        **_BASE_HEADER,
        'latitude': -33.8978,
        'longitude': 151.1899
    },
    'user': _BASE_USER
}

# TRANSACTION RESULT DTO

AUTHN_REQUESTED_WITH_TRANSACTION_RESULT_DTO = AUTHN_REQUESTED_DTO | {
    'transactionResult': {
        'authnFailureReason': None,
        'authnFailureReasonCode': None,
        'authnFailureReasonMessage': None,
        'authnStatus': None,
        'authnTimestamp': FAKE_NOW_IN_MILLIS,
        'transactionStatus': 'PROCESSING'
    }
}

AUTHZ_CODE_GENERATED_UPDATE_TRANSACTION_RESULT_DTO = {
    **AUTHZ_CODE_GENERATED_DTO,
    'transactionResult': {
        'authnFailureReason': None,
        'authnFailureReasonCode': None,
        'authnFailureReasonMessage': None,
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 1690761600,
        'transactionStatus': 'AUTHZ_CODE_DONE'
    }
}

ID_TOKEN_GENERATED_UPDATE_TRANSACTION_RESULT_DTO = {
    **ID_TOKEN_GENERATED_DTO,
    'transactionResult': {
        'authnFailureReason': None,
        'authnFailureReasonCode': None,
        'authnFailureReasonMessage': None,
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 1690761600,
        'transactionStatus': 'ID_TOKEN_DONE'
    }
}

TRANSACTION_WITH_USER_ERROR_TRANSACTION_RESULT_DTO = AUTHN_REQUESTED_WITH_USER_ERROR_DTO | {
    'transactionResult': {
        'authnFailureReason': 'SERVER_ERROR',
        'authnFailureReasonCode': '601666070',
        'authnFailureReasonMessage': 'Internal server error',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': FAKE_NOW_IN_MILLIS,
        'transactionStatus': 'AUTHN_DONE'
    },
}

TRANSACTION_WITH_HEADER_ERROR_TRANSACTION_RESULT_DTO = AUTHN_REQUESTED_WITH_HEADER_ERROR_DTO | {
    'transactionResult': {
        'authnFailureReason': 'SERVER_ERROR',
        'authnFailureReasonCode': '601666070',
        'authnFailureReasonMessage': 'Internal server error',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': FAKE_NOW_IN_MILLIS,
        'transactionStatus': 'AUTHN_DONE'
    },
}

TRANSACTION_TIMEOUT_WITH_TRANSACTION_RESULT_DTO = TRANSACTION_TIMEOUT_DTO | {
    'transactionResult': {
        'authnFailureReason': 'TX_TIMEOUT',
        'authnFailureReasonCode': '601666001',
        'authnFailureReasonMessage': 'Authentication timeout',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': FAKE_NOW_IN_MILLIS,
        'transactionStatus': 'AUTHN_DONE'
    }
}

# PASSWORD_VALIDATED TRANSACTION RESULT DTO

PASSWORD_VALIDATED_UNAUTHORIZED_TRANSACTION_RESULT_DTO = {
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'entityType': 'OIDC_AUTHENTICATION',
    'eventType': 'PASSWORD_VALIDATED',
    'messageId': '54ee5af4-fe86-5f0e-ae7c-07b91e3466be',
    'source': 'flk-core-local-pw-validator',
    'timestamp': 123456789,
    'transactionId': 'abc-123-xyz-456',
    'userId': 12,
    'authnResult': {
        'authnFailureReason': 'PASSWORD_INVALID',
        'authnFailureReasonCode': '701001010',
        'authnFailureReasonMessage': 'Invalid password',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': 123456789,
        'authnTypes': ['password'],
        'userType': 'AUTH_POINT'
    },
    'transactionResult': {
        'authnFailureReason': 'PASSWORD_INVALID',
        'authnFailureReasonCode': '701001010',
        'authnFailureReasonMessage': 'Invalid password',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': FAKE_NOW_IN_MILLIS,
        'transactionStatus': 'AUTHN_DONE'
    }
}

PASSWORD_VALIDATED_UNAUTHORIZED_USER_BLOCKED_TRANSACTION_RESULT_DTO = {
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'entityType': 'OIDC_AUTHENTICATION',
    'eventType': 'PASSWORD_VALIDATED',
    'messageId': '54ee5af4-fe86-5f0e-ae7c-07b91e3466be',
    'source': 'flk-core-local-pw-validator',
    'timestamp': 123456789,
    'transactionId': 'abc-123-xyz-456',
    'userId': 12,
    'authnResult': {
        'authnFailureReason': 'PASSWORD_INVALID',
        'authnFailureReasonCode': '701001010',
        'authnFailureReasonMessage': 'Invalid password',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': 123456789,
        'authnTypes': ['password'],
        'userStatus': 'AUTOMATICALLY_BLOCKED',
        'userType': 'AUTH_POINT'
    },
    'transactionResult': {
        'authnFailureReason': 'PASSWORD_INVALID',
        'authnFailureReasonCode': '701001010',
        'authnFailureReasonMessage': 'Invalid password',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': FAKE_NOW_IN_MILLIS,
        'transactionStatus': 'AUTHN_DONE',
        'userStatus': 'AUTOMATICALLY_BLOCKED'
    }
}

PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_TRANSACTION_RESULT_DTO = {
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'authnResult': {
        'authnFailureReason': 'INVALID_OTP',
        'authnFailureReasonCode': '701002020',
        'authnFailureReasonMessage': 'Invalid OTP',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': 123456789,
        'authnTypes': ['password', 'otp'],
        'tokens': [
            {
                'credentialType': 'TOKEN_SOFTWARE',
                'friendlySerialNumber': 'WG-BC123',
                'status': 'AUTOMATICALLY_BLOCKED'
            }
        ],
        'userType': 'AUTH_POINT'
    },
    'entityType': 'OIDC_AUTHENTICATION',
    'eventType': 'PASSWORD_OTP_VALIDATED',
    'messageId': '54ee5af4-fe86-5f0e-ae7c-07b91e3466be',
    'source': 'flk-core-local-pw-otp-validator',
    'timestamp': 123456789,
    'transactionId': 'abc-123-xyz-456',
    'transactionResult': {
        'authnFailureReason': 'INVALID_OTP',
        'authnFailureReasonCode': '701002020',
        'authnFailureReasonMessage': 'Invalid OTP',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': 1690761600000,
        'tokens': [
            {
                'credentialType': 'TOKEN_SOFTWARE',
                'friendlySerialNumber': 'WG-BC123',
                'status': 'AUTOMATICALLY_BLOCKED'
            }
        ],
        'transactionStatus': 'AUTHN_DONE'
    },
    'userId': 12
}

PASSWORD_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_DONE_DTO = {
    'eventType': 'PASSWORD_VALIDATED',
    'entityType': 'OIDC_AUTHENTICATION',
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'messageId': '54ee5af4-fe86-5f0e-ae7c-07b91e3466be',
    'source': 'flk-core-local-pw-validator',
    'timestamp': 123456789,
    'transactionId': 'abc-123-xyz-456',
    'userId': 12,
    'authnResult': {
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 123456789,
        'authnTypes': ['password'],
        'userType': 'AUTH_POINT'
    },
    'password': {
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 123456789
    },
    'transactionResult': {
        'authnFailureReason': None,
        'authnFailureReasonCode': None,
        'authnFailureReasonMessage': None,
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': FAKE_NOW_IN_MILLIS,
        'transactionStatus': 'AUTHN_DONE'
    }
}

PASSWORD_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_PROCESSING_DTO = {
    'eventType': 'PASSWORD_VALIDATED',
    'entityType': 'OIDC_AUTHENTICATION',
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'messageId': '54ee5af4-fe86-5f0e-ae7c-07b91e3466be',
    'source': 'flk-core-local-pw-validator',
    'timestamp': 123456789,
    'transactionId': 'abc-123-xyz-456',
    'userId': 12,
    'authnResult': {
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 123456789,
        'authnTypes': ['password'],
        'userType': 'AUTH_POINT'
    },
    'password': {
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 123456789
    },
    'transactionResult': {
        'authnFailureReason': None,
        'authnFailureReasonCode': None,
        'authnFailureReasonMessage': None,
        'authnStatus': None,
        'authnTimestamp': FAKE_NOW_IN_MILLIS,
        'transactionStatus': 'PROCESSING'
    }
}

PASSWORD_OTP_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_DTO = {
    'eventType': 'PASSWORD_OTP_VALIDATED',
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'entityType': 'OIDC_AUTHENTICATION',
    'messageId': '54ee5af4-fe86-5f0e-ae7c-07b91e3466be',
    'source': 'flk-core-local-pw-otp-validator',
    'timestamp': 123456789,
    'transactionId': 'abc-123-xyz-456',
    'userId': 12,
    'authnResult': {
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 123456789,
        'authnTypes': ['password', 'otp'],
        'userType': 'AUTH_POINT'
    },
    'otp': {
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 123456789
    },
    'password': {
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 123456789
    },
    'transactionResult': {
        'authnFailureReason': None,
        'authnFailureReasonCode': None,
        'authnFailureReasonMessage': None,
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': FAKE_NOW_IN_MILLIS,
        'transactionStatus': 'AUTHN_DONE'
    }
}

_PASSKEY_DATA = {
    'credentialId': 'repUs20QulcXyFNB3hKcMC6G3yOY3ZfoUG6-S7LPm8w',
    'friendlyCredentialId': 'PK-LPM8W',
    'status': 'ACTIVE',
    'credentialType': 'PASSKEY',
    'signCount': 0,
    'lastUpdatedOn': 1770227062424,
    'lastSuccessfulAuthentication': 1770227062424,
    'createdOn': 1769634526616,
    'deviceType': 'multi_device',
    'backedUp': True
}

PASSKEY_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_DONE_DTO = {
    'eventType': 'PASSKEY_VALIDATED',
    'entityType': 'OIDC_AUTHENTICATION',
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'messageId': '54ee5af4-fe86-5f0e-ae7c-07b91e3466be',
    'source': 'flk-core-passkey-validator',
    'timestamp': 123456789,
    'transactionId': 'abc-123-xyz-456',
    'userId': 12,
    'authnResult': {
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 123456789,
        'authnTypes': ['passkey'],
        'userType': 'AUTH_POINT',
        'passkey': _PASSKEY_DATA
    },
    'passkey': {
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 123456789
    },
    'transactionResult': {
        'authnFailureReason': None,
        'authnFailureReasonCode': None,
        'authnFailureReasonMessage': None,
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': FAKE_NOW_IN_MILLIS,
        'transactionStatus': 'AUTHN_DONE',
        'passkey': _PASSKEY_DATA
    }
}

PASSKEY_VALIDATED_AUTHORIZED_TRANSACTION_RESULT_PROCESSING_DTO = {
    'eventType': 'PASSKEY_VALIDATED',
    'entityType': 'OIDC_AUTHENTICATION',
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'messageId': '54ee5af4-fe86-5f0e-ae7c-07b91e3466be',
    'source': 'flk-core-passkey-validator',
    'timestamp': 123456789,
    'transactionId': 'abc-123-xyz-456',
    'userId': 12,
    'authnResult': {
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 123456789,
        'authnTypes': ['passkey'],
        'userType': 'AUTH_POINT',
        'passkey': _PASSKEY_DATA
    },
    'passkey': {
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 123456789
    },
    'transactionResult': {
        'authnFailureReason': None,
        'authnFailureReasonCode': None,
        'authnFailureReasonMessage': None,
        'authnStatus': None,
        'authnTimestamp': FAKE_NOW_IN_MILLIS,
        'transactionStatus': 'PROCESSING',
        'passkey': _PASSKEY_DATA
    }
}

PASSKEY_VALIDATED_UNAUTHORIZED_TRANSACTION_RESULT_DTO = {
    'eventType': 'PASSKEY_VALIDATED',
    'entityType': 'OIDC_AUTHENTICATION',
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'messageId': '54ee5af4-fe86-5f0e-ae7c-07b91e3466be',
    'source': 'flk-core-passkey-validator',
    'timestamp': 123456789,
    'transactionId': 'abc-123-xyz-456',
    'userId': 12,
    'authnResult': {
        'authnFailureReason': 'INVALID_PASSKEY_AUTHN',
        'authnFailureReasonCode': '701017064',
        'authnFailureReasonMessage': 'Invalid passkey authentication',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': 123456789,
        'authnTypes': ['passkey'],
        'userType': 'AUTH_POINT',
        'passkey': _PASSKEY_DATA
    },
    'transactionResult': {
        'authnFailureReason': 'INVALID_PASSKEY_AUTHN',
        'authnFailureReasonCode': '701017064',
        'authnFailureReasonMessage': 'Invalid passkey authentication',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': FAKE_NOW_IN_MILLIS,
        'transactionStatus': 'AUTHN_DONE',
        'passkey': _PASSKEY_DATA
    }
}
