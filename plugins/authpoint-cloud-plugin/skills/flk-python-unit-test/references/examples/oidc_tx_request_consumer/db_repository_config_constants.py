# DTOs

from tests.transaction.consumer.oidc_tx_request_consumer.sqs_message_constants import (
    TRANSACTION_TIMEOUT_DTO, PASSWORD_VALIDATED_UNAUTHORIZED_DTO, PASSWORD_VALIDATED_AUTHORIZED_DTO,
    PASSWORD_OTP_VALIDATED_AUTHORIZED_DTO, PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_DTO, AUTHN_REQUESTED_DTO)

AUTHN_REQUESTED_WITH_TRANSACTION_RESULT_DTO = AUTHN_REQUESTED_DTO | {
    'transactionResult': {
        'authnFailureReason': None,
        'authnFailureReasonCode': None,
        'authnFailureReasonMessage': None,
        'authnStatus': None,
        'authnTimestamp': 1690761600,
        'transactionStatus': 'PROCESSING'
    }
}

TRANSACTION_TIMEOUT_WITH_TRANSACTION_RESULT_DTO = TRANSACTION_TIMEOUT_DTO | {
    'transactionResult': {
        'authnFailureReason': 'TX_TIMEOUT',
        'authnFailureReasonCode': '601666001',
        'authnFailureReasonMessage': 'Authentication timeout',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': 1690761600,
        'transactionStatus': 'AUTHN_DONE'
    }
}

PASSWORD_VALIDATED_UNAUTHORIZED_WITH_TRANSACTION_RESULT_DTO = PASSWORD_VALIDATED_UNAUTHORIZED_DTO | {
    'transactionResult': {
        'authnFailureReason': 'INVALID_PASSWORD',
        'authnFailureReasonCode': '701010010',
        'authnFailureReasonMessage': 'Invalid password',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': 1690761600,
        'transactionStatus': 'AUTHN_DONE'
    }
}

PASSWORD_VALIDATED_AUTHORIZED_WITH_TRANSACTION_RESULT_DTO = PASSWORD_VALIDATED_AUTHORIZED_DTO | {
    'password': {
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 123456789
    },
    'transactionResult': {
        'authnFailureReason': None,
        'authnFailureReasonCode': None,
        'authnFailureReasonMessage': None,
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 1690761600,
        'transactionStatus': 'AUTHN_DONE'
    }
}

PASSWORD_OTP_VALIDATED_AUTHORIZED_WITH_TRANSACTION_RESULT_DTO = PASSWORD_OTP_VALIDATED_AUTHORIZED_DTO | {
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
        'authnTimestamp': 1690761600,
        'transactionStatus': 'AUTHN_DONE'
    }
}

PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_TRANSACTION_RESULT_DTO = \
    PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_DTO | {
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
        }
    }

# DDB KEYS

TRANSACTION_PARTITION_KEY = 'WGC-0'

AUTHENTICATION_PARTITION_KEY = 'WGC-123-abc'

LUFFY_TRANSACTION_SORT_KEY = 'TRANSACTION#abc-123-xyz-456'

ZORO_TRANSACTION_SORT_KEY = 'TRANSACTION#abc-333-xyz-666'

AUTHN_METADATA_PARTITION_KEY = 'WGC-0#LAST_SUCCESSFUL_AUTHENTICATION'

AUTHN_METADATA_SORT_KEY = 'USER#12'

# DDB MODELS

TRANSACTION_AUTHN_DONE = {
    'txStatusGsi1': 'TRANSACTION#abc-123-xyz-456',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'accountId': 'WGC-0',
    'userId': 12,
    'transactionResult': {
        'authnFailureReason': None,
        'authnFailureReasonCode': None,
        'authnFailureReasonMessage': None,
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 1690761600,
        'transactionStatus': 'AUTHN_DONE'
    },
    'softDeletedTtl': 1632961500,
    'header': {
        'accountId': 'WGC-0',
        'transactionId': 'abc-123-xyz-456',
        'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
        'applicationType': 'FIREWAN',
        'clientId': '123-abc',
        'clientIp': '1.0.0.1',
        'clientSecret': 'client_secret',
        'friendlyType': 'WG_INTERNAL',
        'latitude': -33.8978,
        'longitude': 151.1899,
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

TRANSACTION_WITH_ERROR_MODEL = {
    'transactionResult': {
        'transactionStatus': 'AUTHN_DONE',
        'authnStatus': 'UNAUTHORIZED',
        'authnFailureReason': 'INVALID_TRANSACTION_MISSING_FIELDS',
        'authnTimestamp': 12334567,
        'lastUpdatedOn': 12334567
    },
    'softDeletedTtl': 1632961500,
    'header': {
        'accountId': 'WGC-0',
        'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
        'applicationType': 'FIREWAN',
        'clientId': '123-abc',
        'clientIp': '1.0.0.1',
        'clientSecret': 'client_secret',
        'friendlyType': 'WG_INTERNAL',
        'nonce': '1599046102647-dv4',
        'redirectUri': 'http://localhost:4200/callback',
        'resourceId': 1,
        'issuer': 'https://oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/ACC-1456',
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

TRANSACTION_TIMEOUT_MODEL = {
    'transactionResult': {
        'authnFailureReason': 'TX_TIMEOUT',
        'authnFailureReasonCode': '601666001',
        'authnFailureReasonMessage': 'Authentication timeout',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': 1690761600,
        'transactionStatus': 'AUTHN_DONE'
    }
}

PASSWORD_VALIDATED_UNAUTHORIZED_MODEL = {
    'transactionResult': {
        'authnFailureReason': 'INVALID_PASSWORD',
        'authnFailureReasonCode': '701010010',
        'authnFailureReasonMessage': 'Invalid password',
        'authnStatus': 'UNAUTHORIZED',
        'authnTimestamp': 1690761600,
        'transactionStatus': 'AUTHN_DONE'
    }
}

PASSWORD_VALIDATED_AUTHORIZED_MODEL = {
    'password': {
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 123456789
    },
    'transactionResult': {
        'authnFailureReason': None,
        'authnFailureReasonCode': None,
        'authnFailureReasonMessage': None,
        'authnStatus': 'AUTHORIZED',
        'authnTimestamp': 1690761600,
        'transactionStatus': 'AUTHN_DONE'
    }
}

PASSWORD_OTP_VALIDATED_AUTHORIZED_MODEL = {
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
        'authnTimestamp': 1690761600,
        'transactionStatus': 'AUTHN_DONE'
    }
}

PASSWORD_OTP_VALIDATED_UNAUTHORIZED_MODEL = {
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
    }
}

AUTHN_METADATA_MODEL = {
    'accountId': 'WGC-0',
    'authnTimestamp': 1690761600,
    'userId': 12,
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'transactionId': 'abc-123-xyz-456',
    'latitude': -33.8978,
    'longitude': 151.1899,
    'resourceType': 'OIDC',
    'expirationTimeInMillis': 1633046400000,
    'softDeletedTtl': 1633046400,
}
