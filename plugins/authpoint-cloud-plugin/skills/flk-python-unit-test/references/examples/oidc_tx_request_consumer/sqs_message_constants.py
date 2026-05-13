# API EVENTS

AUTHN_REQUESTED_EVENT = {
    'Records': [
        {
            'messageId': 'ca9bc51b-ba57-4a78-a337-b26e414085e5',
            'receiptHandle': 'AQEBzQ8hlse0NuHMp1GlIUUFJAQNyklkK/jy53M/d8aiZ8LrFEjTS8NELYbZLKW+ZTjKjkR5xVxkvNeTu9aKhy/9bBvFnlp6u/LTeaYLrsrD9eJGB92tA/dcoC+z/vehkycTTTO7lVoFsctmG696BWw51fJqHCAYqIQQlZ+4FIcKjLpUxlyefd7zN/9iebitdoE+JvDqZ1lahe18tlA4XhRPIhS/rV4VhiOwb265Y4jIcRoU4w6640AQk55ywggAtpHU2l1gi+5ahusrMLdDRkozidrjorLH5Rp3Ylpjz7aTUPU=',
            'body': '{\n  "type":"OIDC_AUTHN_REQUESTED",\n  "entityType":"OIDC_TRANSACTION",\n  "source" : "flk-oidc-authn-api",\n  "timestamp":12334567,\n  "data":{\n    "accountId": "WGC-0",\n    "userId": 12,\n    "transactionId": "abc-123-xyz-456",\n    "header": {\n      "accountId": "WGC-0",\n    "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a",\n      "transactionId": "abc-123-xyz-456",\n      "resourceId": 1,\n      "resourceName": "my firewan",\n      "resourceType":"OIDC",\n      "latitude": -33.8978,\n      "longitude": 151.1899,\n      "friendlyType":"WG_INTERNAL",\n      "applicationType" : "FIREWAN",\n      "clientId": "123-abc",\n      "clientSecret": "client_secret",\n      "clientIp": "1.0.0.1",\n      "redirectUri": "http://localhost:4200/callback",\n      "state": "1599045135410-jFe",\n      "nonce": "1599046102647-dv4"\n    },\n    "user": {\n      "userId": 12,\n      "isMfa": false,\n      "firstName": "luffy",\n      "lastName": "monkey d.",\n      "username": "luffy",\n      "email": "luffy@email.com",\n      "loginType": "USERNAME",\n      "authnTypes": ["password", "push"],\n      "userType": "AUTH_POINT"\n    }\n  }\n}',
        }
    ]
}

AUTHZ_CODE_GENERATED_EVENT = {
    'Records': [
        {
            'messageId': 'ca9bc51b-ba57-4a78-a337-b26e414085e5',
            'receiptHandle': 'AQEBzQ8hlse0NuHMp1GlIUUFJAQNyklkK/jy53M/d8aiZ8LrFEjTS8NELYbZLKW+ZTjKjkR5xVxkvNeTu9aKhy/9bBvFnlp6u/LTeaYLrsrD9eJGB92tA/dcoC+z/vehkycTTTO7lVoFsctmG696BWw51fJqHCAYqIQQlZ+4FIcKjLpUxlyefd7zN/9iebitdoE+JvDqZ1lahe18tlA4XhRPIhS/rV4VhiOwb265Y4jIcRoU4w6640AQk55ywggAtpHU2l1gi+5ahusrMLdDRkozidrjorLH5Rp3Ylpjz7aTUPU=',
            'body': '{\n  "type":"OIDC_AUTHZ_CODE_GENERATED",\n  "entityType":"OIDC_TRANSACTION",\n  "source" : "flk-oidc-authn-api",\n  "timestamp":12334567,\n  "data":{\n    "accountId": "WGC-0",\n    "userId": 12,\n    "transactionId": "abc-123-xyz-456",\n    "header": {\n      "accountId": "WGC-0",\n    "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a",\n      "transactionId": "abc-123-xyz-456",\n      "resourceId": 1,\n      "resourceName": "my firewan",\n      "resourceType":"OIDC",\n      "latitude": -33.8978,\n      "longitude": 151.1899,\n      "friendlyType":"WG_INTERNAL",\n      "applicationType" : "FIREWAN",\n      "clientId": "123-abc",\n      "clientSecret": "client_secret",\n      "clientIp": "1.0.0.1",\n      "redirectUri": "http://localhost:4200/callback",\n      "state": "1599045135410-jFe",\n      "nonce": "1599046102647-dv4"\n    },\n    "user": {\n      "userId": 12,\n      "isMfa": false,\n      "firstName": "luffy",\n      "lastName": "monkey d.",\n      "username": "luffy",\n      "email": "luffy@email.com",\n      "loginType": "USERNAME",\n      "authnTypes": ["password", "push"],\n      "userType": "AUTH_POINT"\n    }\n  }\n}',
        }
    ]
}

TRANSACTION_TIMEOUT_EVENT = {
    'Records': [
        {
            'messageId': 'c8232bb5-fcdf-401f-b6cf-7ce23156146f',
            'receiptHandle': 'AQEB6TjoekJrTNmu+Vgn1DMowBNiHlnzNaZeYMPzDypU4ttFY74AJm/9IFwymLzYrz/b/lYItdylcCxEOV7GImxty58ENBvzl1o/L9ladimSCxZkh92Gzb4vLkiLP4Rtt9icifWgfqADp3hUX3yt8Pz1VwaRck8aCmUQQskJ/zc8ThsWWfnhxE3ZLEg5I2O59OAyeHEY1CY8tHMHcU1b8q2rQlSpMUbfbuPYalFk44KDuDOtqE0j7yNd5/tXFiDcM4vGbOG9aKsswST0meQYyWnB+uFzhWPFJso0mSo5a1sqEis=',
            'body': '{\n  "type":"OIDC_TRANSACTION_TIMEOUT",\n  "entityType":"OIDC_TRANSACTION",\n  "source" : "flk-oidc-tx-timeout-publisher",\n  "timestamp":12334567,\n  "data":{\n    "accountId": "WGC-0",\n    "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a",\n    "userId": 12,\n    "transactionId": "abc-123-xyz-456"\n  }\n}',
        }
    ]
}

# CORE EVENTS

PASSWORD_VALIDATED_EVENT = {
    'Records': [
        {
            'messageId': '9a214fef-594f-4bbc-bee1-eaa9b9703fa1',
            'receiptHandle': 'AQEB0ZvyyRgGBcgM6BS9uafILHuULd30LKRdGOgDLWahq1ktJReduQn1s7g5J+rENxbvF6vRJ8z52Zbtj6DJQFrNfAp5H7Mh0IrstAE/H7uNxzoW8/aD1CXa+eYLqcmJ3sqV6vBmI2NyQmBabn3NMjbpicldbn+SzOqGBQJnfx0Z5QB6m0wg9VeKQeMIPw9xTyCokGekaCFSmi/BEDGaUhMu7rR5OQ542BP8L/bqJa5d8b9DPokFszWz6bYyOvA9utd+Fch1I5Byu3B+waJVTMnl3Mm9tIypK2RhY8NOEOAeAlk=',
            'body': '{\"Type\":\"Notification\",\"MessageId\":\"54ee5af4-fe86-5f0e-ae7c-07b91e3466be\",\"TopicArn\":\"arn:aws:sns:us-west-2:093992175903:dev-unified-config-notification\",\"Message\":\"{\\\"type\\\":\\\"PASSWORD_VALIDATED\\\",\\\"entityType\\\":\\\"OIDC_AUTHENTICATION\\\",\\\"timestamp\\\":123456789,\\\"source\\\":\\\"flk-core-local-pw-validator\\\",\\\"data\\\":{\\\"accountId\\\":\\\"WGC-123-abc\\\",\\\"chainId\\\":\\\"b09165ce-9afe-4585-8ccd-f1a08c25555a\\\",\\\"userId\\\":12,\\\"transactionId\\\":\\\"abc-123-xyz-456\\\",\\\"authnResult\\\":{\\\"authnTypes\\\":[\\\"password\\\"],\\\"userType\\\":\\\"AUTH_POINT\\\",\\\"authnTimestamp\\\":123456789,\\\"authnStatus\\\":\\\"UNAUTHORIZED\\\",\\\"authnFailureReason\\\":\\\"PASSWORD_INVALID\\\",\\\"authnFailureReasonCode\\\":\\\"701001010\\\",\\\"authnFailureReasonMessage\\\":\\\"Invalid password\\\"}}}\",\"Timestamp\":\"2023-08-09T18:44:02.177Z\",\"SignatureVersion\":\"1\",\"Signature\":\"k6XYXQv8BCYrPl6Zv7mDR1\",\"SigningCertURL\":\"SimpleNotificationService-01d088a6f77103d0fe307c0069e40ed6.pem\",\"UnsubscribeURL\":\"UnsubscribeURL\"}',
        }
    ]
}

PASSWORD_VALIDATED_USER_AUTO_BLOCKED_EVENT = {
    'Records': [
        {
            'messageId': '9a214fef-594f-4bbc-bee1-eaa9b9703fa1',
            'receiptHandle': 'AQEB0ZvyyRgGBcgM6BS9uafILHuULd30LKRdGOgDLWahq1ktJReduQn1s7g5J+rENxbvF6vRJ8z52Zbtj6DJQFrNfAp5H7Mh0IrstAE/H7uNxzoW8/aD1CXa+eYLqcmJ3sqV6vBmI2NyQmBabn3NMjbpicldbn+SzOqGBQJnfx0Z5QB6m0wg9VeKQeMIPw9xTyCokGekaCFSmi/BEDGaUhMu7rR5OQ542BP8L/bqJa5d8b9DPokFszWz6bYyOvA9utd+Fch1I5Byu3B+waJVTMnl3Mm9tIypK2RhY8NOEOAeAlk=',
            'body': '{\"Type\":\"Notification\",\"MessageId\":\"54ee5af4-fe86-5f0e-ae7c-07b91e3466be\",\"TopicArn\":\"arn:aws:sns:us-west-2:093992175903:dev-unified-config-notification\",\"Message\":\"{\\\"type\\\":\\\"PASSWORD_VALIDATED\\\",\\\"entityType\\\":\\\"OIDC_AUTHENTICATION\\\",\\\"timestamp\\\":123456789,\\\"source\\\":\\\"flk-core-local-pw-validator\\\",\\\"data\\\":{\\\"accountId\\\":\\\"WGC-123-abc\\\",\\\"chainId\\\":\\\"b09165ce-9afe-4585-8ccd-f1a08c25555a\\\",\\\"userId\\\":12,\\\"transactionId\\\":\\\"abc-123-xyz-456\\\",\\\"authnResult\\\":{\\\"authnTypes\\\":[\\\"password\\\"],\\\"userStatus\\\":\\\"AUTOMATICALLY_BLOCKED\\\",\\\"userType\\\":\\\"AUTH_POINT\\\",\\\"authnTimestamp\\\":123456789,\\\"authnStatus\\\":\\\"UNAUTHORIZED\\\",\\\"authnFailureReason\\\":\\\"PASSWORD_INVALID\\\",\\\"authnFailureReasonCode\\\":\\\"701001010\\\",\\\"authnFailureReasonMessage\\\":\\\"Invalid password\\\"}}}\",\"Timestamp\":\"2023-08-09T18:44:02.177Z\",\"SignatureVersion\":\"1\",\"Signature\":\"k6XYXQv8BCYrPl6Zv7mDR1\",\"SigningCertURL\":\"SimpleNotificationService-01d088a6f77103d0fe307c0069e40ed6.pem\",\"UnsubscribeURL\":\"UnsubscribeURL\"}',
        }
    ]
}

PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_EVENT = {
    'Records': [
        {
            'messageId': '9a214fef-594f-4bbc-bee1-eaa9b9703fa1',
            'receiptHandle': 'AQEB0ZvyyRgGBcgM6BS9uafILHuULd30LKRdGOgDLWahq1ktJReduQn1s7g5J+rENxbvF6vRJ8z52Zbtj6DJQFrNfAp5H7Mh0IrstAE/H7uNxzoW8/aD1CXa+eYLqcmJ3sqV6vBmI2NyQmBabn3NMjbpicldbn+SzOqGBQJnfx0Z5QB6m0wg9VeKQeMIPw9xTyCokGekaCFSmi/BEDGaUhMu7rR5OQ542BP8L/bqJa5d8b9DPokFszWz6bYyOvA9utd+Fch1I5Byu3B+waJVTMnl3Mm9tIypK2RhY8NOEOAeAlk=',
            'body': '{\"Type\":\"Notification\",\"MessageId\":\"54ee5af4-fe86-5f0e-ae7c-07b91e3466be\",\"TopicArn\":\"arn:aws:sns:us-west-2:093992175903:dev-unified-config-notification\",\"Message\":\"{\\\"type\\\":\\\"PASSWORD_OTP_VALIDATED\\\",\\\"entityType\\\":\\\"OIDC_AUTHENTICATION\\\",\\\"timestamp\\\":123456789,\\\"source\\\":\\\"flk-core-local-pw-otp-validator\\\",\\\"data\\\":{\\\"accountId\\\":\\\"WGC-123-abc\\\",\\\"chainId\\\":\\\"b09165ce-9afe-4585-8ccd-f1a08c25555a\\\",\\\"userId\\\":12,\\\"transactionId\\\":\\\"abc-123-xyz-456\\\",\\\"authnResult\\\":{\\\"authnTypes\\\":[\\\"password\\\", \\\"otp\\\"],\\\"userType\\\":\\\"AUTH_POINT\\\",\\\"authnTimestamp\\\":123456789,\\\"authnStatus\\\":\\\"UNAUTHORIZED\\\",\\\"authnFailureReason\\\":\\\"INVALID_OTP\\\",\\\"authnFailureReasonCode\\\":\\\"701002020\\\",\\\"authnFailureReasonMessage\\\":\\\"Invalid OTP\\\",\\\"tokens\\\": [{\\\"friendlySerialNumber\\\": \\\"WG-BC123\\\", \\\"status\\\": \\\"AUTOMATICALLY_BLOCKED\\\", \\\"credentialType\\\": \\\"TOKEN_SOFTWARE\\\"}]}}}\",\"Timestamp\":\"2023-08-09T18:44:02.177Z\",\"SignatureVersion\":\"1\",\"Signature\":\"k6XYXQv8BCYrPl6Zv7mDR1\",\"SigningCertURL\":\"SimpleNotificationService-01d088a6f77103d0fe307c0069e40ed6.pem\",\"UnsubscribeURL\":\"UnsubscribeURL\"}',
        }
    ]
}

# DTOs

AUTHN_REQUESTED_DTO = {
    'eventType': 'OIDC_AUTHN_REQUESTED',
    'entityType': 'OIDC_TRANSACTION',
    'accountId': 'WGC-0',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'messageId': 'ca9bc51b-ba57-4a78-a337-b26e414085e5',
    'source': 'flk-oidc-authn-api',
    'timestamp': 12334567,
    'header': {
        'accountId': 'WGC-0',
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

AUTHZ_CODE_GENERATED_DTO = {
    'eventType': 'OIDC_AUTHZ_CODE_GENERATED',
    'entityType': 'OIDC_TRANSACTION',
    'accountId': 'WGC-0',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'messageId': 'ca9bc51b-ba57-4a78-a337-b26e414085e5',
    'source': 'flk-oidc-authn-api',
    'timestamp': 12334567,
    'header': {
        'accountId': 'WGC-0',
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

ID_TOKEN_GENERATED_DTO = {
    'eventType': 'OIDC_ID_TOKEN_GENERATED',
    'entityType': 'OIDC_TRANSACTION',
    'accountId': 'WGC-0',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'messageId': 'ca9bc51b-ba57-4a78-a337-b26e414085e5',
    'source': 'flk-oidc-authn-api',
    'timestamp': 12334567,
    'header': {
        'accountId': 'WGC-0',
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

TRANSACTION_TIMEOUT_DTO = {
    'eventType': 'OIDC_TRANSACTION_TIMEOUT',
    'entityType': 'OIDC_TRANSACTION',
    'accountId': 'WGC-0',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'messageId': 'c8232bb5-fcdf-401f-b6cf-7ce23156146f',
    'source': 'flk-oidc-tx-timeout-publisher',
    'timestamp': 12334567
}

PASSWORD_VALIDATED_UNAUTHORIZED_DTO = {
    'eventType': 'PASSWORD_VALIDATED',
    'entityType': 'OIDC_AUTHENTICATION',
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'messageId': '54ee5af4-fe86-5f0e-ae7c-07b91e3466be',
    'source': 'flk-core-local-pw-validator',
    'timestamp': 123456789,
    'authnResult': {
        'authnTypes': ['password'],
        'authnStatus': 'UNAUTHORIZED',
        'userType': 'AUTH_POINT',
        'authnFailureReason': 'PASSWORD_INVALID',
        'authnFailureReasonCode': '701001010',
        'authnFailureReasonMessage': 'Invalid password',
        'authnTimestamp': 123456789
    }
}

PASSWORD_VALIDATED_UNAUTHORIZED_USER_BLOCKED_DTO = {
    'eventType': 'PASSWORD_VALIDATED',
    'entityType': 'OIDC_AUTHENTICATION',
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'messageId': '54ee5af4-fe86-5f0e-ae7c-07b91e3466be',
    'source': 'flk-core-local-pw-validator',
    'timestamp': 123456789,
    'authnResult': {
        'authnTypes': ['password'],
        'userStatus': 'AUTOMATICALLY_BLOCKED',
        'authnStatus': 'UNAUTHORIZED',
        'userType': 'AUTH_POINT',
        'authnFailureReason': 'PASSWORD_INVALID',
        'authnFailureReasonCode': '701001010',
        'authnFailureReasonMessage': 'Invalid password',
        'authnTimestamp': 123456789
    }
}

PASSWORD_OTP_VALIDATED_UNAUTHORIZED_TOKEN_BLOCKED_DTO = {
    'eventType': 'PASSWORD_OTP_VALIDATED',
    'entityType': 'OIDC_AUTHENTICATION',
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'messageId': '54ee5af4-fe86-5f0e-ae7c-07b91e3466be',
    'source': 'flk-core-local-pw-otp-validator',
    'timestamp': 123456789,
    'authnResult': {
        'authnTypes': ['password', 'otp'],
        'authnStatus': 'UNAUTHORIZED',
        'userType': 'AUTH_POINT',
        'authnFailureReason': 'INVALID_OTP',
        'authnFailureReasonCode': '701002020',
        'authnFailureReasonMessage': 'Invalid OTP',
        'authnTimestamp': 123456789,
        'tokens': [
            {
                'friendlySerialNumber': 'WG-BC123',
                'status': 'AUTOMATICALLY_BLOCKED',
                'credentialType': 'TOKEN_SOFTWARE'
            }
        ]
    }
}

PASSWORD_VALIDATED_AUTHORIZED_DTO = {
    'eventType': 'PASSWORD_VALIDATED',
    'entityType': 'OIDC_AUTHENTICATION',
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'messageId': '54ee5af4-fe86-5f0e-ae7c-07b91e3466be',
    'source': 'flk-core-local-pw-validator',
    'timestamp': 123456789,
    'authnResult': {
        'authnTypes': ['password'],
        'authnStatus': 'AUTHORIZED',
        'userType': 'AUTH_POINT',
        'authnTimestamp': 123456789
    }
}

PASSWORD_OTP_VALIDATED_AUTHORIZED_DTO = {
    'eventType': 'PASSWORD_OTP_VALIDATED',
    'entityType': 'OIDC_AUTHENTICATION',
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'userId': 12,
    'transactionId': 'abc-123-xyz-456',
    'messageId': '54ee5af4-fe86-5f0e-ae7c-07b91e3466be',
    'source': 'flk-core-local-pw-otp-validator',
    'timestamp': 123456789,
    'authnResult': {
        'authnTypes': ['password', 'otp'],
        'authnStatus': 'AUTHORIZED',
        'userType': 'AUTH_POINT',
        'authnTimestamp': 123456789
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

PASSKEY_VALIDATED_AUTHORIZED_DTO = {
    'eventType': 'PASSKEY_VALIDATED',
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'entityType': 'OIDC_AUTHENTICATION',
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
    }
}

PASSKEY_VALIDATED_UNAUTHORIZED_DTO = {
    'eventType': 'PASSKEY_VALIDATED',
    'accountId': 'WGC-123-abc',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'entityType': 'OIDC_AUTHENTICATION',
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
    }
}
