# DTOs
BASE_DTO = {
    'accountId': 'WGC-0',
    'authnContextId': 'e761cb08-bf00-475f-992a-11ae2ac488f1',
    'chainId': 'b09165ce-9afe-4585-8ccd-f1a08c25555a',
    'browser': 'Firefox',
    'city': 'Santa Rita do Sapucai',
    'userId': 12,
    'userType': 'AUTH_POINT',
    'loginType': 'EMAIL',
    'resourceName': 'aaaa',
    'clientAuthz': {'accountId': 'WGC-123-abc',
                    'authnContextId': 'xpto123',
                    'city': 'Washington',
                    'contextType': 'CLIENT_AUTHZ',
                    'country': 'US',
                    'countryName': 'United States',
                    'oidcClient': {'applicationType': 'FIREWAN',
                                   'clientId': '123-456-ABC',
                                   'clientIp': '1.0.0.1',
                                   'clientName': 'Client Name',
                                   'clientSecret': 'client_secret',
                                   'customClaims': [{'name': 'preferred_username',
                                                     'value': 'username'},
                                                    {'name': 'groups',
                                                     'value': 'groups'}],
                                   'friendlyType': 'WG_INTERNAL',
                                   'issuer': 'some-url.com',
                                   'nonce': '1599046102647-dv4',
                                   'redirectUri': 'example.com/callback',
                                   'resourceId': 123,
                                   'resourceName': 'aaaa',
                                   'resourceType': 'OIDC',
                                   'responseType': 'id_token',
                                   'state': '1599045135410-jFe'},
                    'partitionKey': 'WGC-123-abc#AUTHN_CONTEXT#xpto123',
                    'regionName': 'Virginia',
                    'softDeletedTtl': 1715563960001,
                    'sortKey': 'CLIENT_AUTHZ#123-456-ABC'},
    'clientId': '089536f9-b48e-4b22-9f22-a71149543bd3',
    'sourceIp': '0.0.0.0',
    'cookieHeader': '_rollupGa=GA1.2.701387687.1683555256; x=y; '
                    'authpoint_sso_session=eyJ1c2VySGFzaCI6ICIwZmNlMmU0Yi05ZGI1LTNiN2YtYWVlYS1mZGZjNjJiOTM3NGUiLCAic2Vzc2lvbklkIjogIjU3YWJmZjAyLTk0MzQtNDk0Yy1hZDMwLTRjNDU0MmYxYTk4YSJ9; '
                    'authpoint_sso_context=eyJhdXRobkNvbnRleHRJZCI6ICJlNzYxY2IwOC1iZjAwLTQ3NWYtOTkyYS0xMWFlMmFjNDg4ZjEiLCAiY2xpZW50SWQiOiAiMDg5NTM2ZjktYjQ4ZS00YjIyLTlmMjItYTcxMTQ5NTQzYmQzIn0=; '
                    'Path=/; Secure; HttpOnly;',
    'countryName': 'Brazil',
    'extendedRequestId': '123',
    'httpMethod': 'POST',
    'login': 'johndoe',
    'os': 'Windows',
    'password': 'strong-password#01',
    'regionName': 'Minas Gerais',
    'requestId': '123',
    'transactionId': 'txid12345',
    'userConfig': {'accountId': 'WGC-0',
                   'authnContextId': 'e761cb08-bf00-475f-992a-11ae2ac488f1',
                   'city': 'Washington',
                   'contextType': 'USER_CONFIG',
                   'country': 'US',
                   'countryName': 'United States',
                   'expirationTimeInMillis': 4083592109000,
                   'regionName': 'Virginia',
                   'softDeleteTtl': 0,
                   'user': {'authnTypesOptions': ['password',
                                                  'push',
                                                  'qrcode',
                                                  'otp'],
                            'email': 'luffy@email.com',
                            'firstName': 'luffy',
                            'groups': [1, 2, 3],
                            'isMfa': False,
                            'lastName': 'monkey d.',
                            'loginType': 'EMAIL',
                            'overAllocated': False,
                            'quarantine': False,
                            'status': 'ACTIVE',
                            'userId': 12,
                            'userType': 'AUTH_POINT',
                            'username': 'luffy'},
                   'userConfigResult': {'userConfigSuccess': True},
                   'userId': 12}
}

PASSWORD_ONLY_DTO = {
    **BASE_DTO | {
        'authnTypes': ['password']
    }
}

PUSH_DTO = {
    **BASE_DTO | {
        'authnTypes': ['push']
    }
}

QRCODE_DTO = {
    **BASE_DTO | {
        'authnTypes': ['qrcode'],
        'qrcodeResponse': '123456',
        'qrcodeTransactionId': '3ec6abed-633c-4fa8-9613-418224bb6025'
    }
}

OTP_DTO = {
    **BASE_DTO | {
        'authnTypes': ['otp'],
        'otp': '098765'
    }
}

PASSKEY_DTO = {
    **BASE_DTO | {
        'authnTypes': ['passkey'],
        'passkey': {
            'id': 'VmZ2kDoJXaDLbXL17G5Dqw'
        },
        'passkeyTransactionId': '111-111'
    }
}

AUTHN_CODE_DTO = {
    **BASE_DTO | {
        'authnTypes': ['authncode'],
        'forgotTokenAuthnCode': '111765',
        'forgotTokenRandomChallenge': '234567'
    }
}

AZURE_AD_PASSWORD_DTO = {
    **BASE_DTO | {
        'userType': 'AZURE_AD',
        'authnTypes': ['password'],
        'userConfig': {'user': {'userType': 'AZURE_AD'}}
    }
}

AZURE_AD_PASSWORD_PUSH_DTO = {
    **BASE_DTO | {
        'userType': 'AZURE_AD',
        'authnTypes': ['password', 'push'],
        'userConfig': {'user': {'userType': 'AZURE_AD'}}
    }
}

AZURE_AD_PASSWORD_QRCODE_DTO = {
    **BASE_DTO | {
        'userType': 'AZURE_AD',
        'authnTypes': ['password', 'qrcode'],
        'userConfig': {'user': {'userType': 'AZURE_AD'}},
        'qrcodeResponse': '123456',
        'qrcodeTransactionId': '3ec6abed-633c-4fa8-9613-418224bb6025'
    }
}

AZURE_AD_PASSWORD_OTP_DTO = {
    **BASE_DTO | {
        'userType': 'AZURE_AD',
        'authnTypes': ['password', 'otp'],
        'userConfig': {'user': {'userType': 'AZURE_AD'}},
        'otp': '098765'
    }
}

AZURE_AD_PASSWORD_AUTHN_CODE_DTO = {
    **BASE_DTO | {
        'userType': 'AZURE_AD',
        'authnTypes': ['password', 'authncode'],
        'userConfig': {'user': {'userType': 'AZURE_AD'}},
        'forgotTokenAuthnCode': '111765',
        'forgotTokenRandomChallenge': '234567'
    }
}

LDAP_PASSWORD_DTO = {
    **BASE_DTO | {
        'userType': 'LDAP',
        'authnTypes': ['password'],
        'userConfig': {'user': {'userType': 'LDAP'}}
    }
}

LDAP_PASSWORD_PUSH_DTO = {
    **BASE_DTO | {
        'userType': 'LDAP',
        'authnTypes': ['password', 'push'],
        'userConfig': {'user': {'userType': 'LDAP'}}
    }
}

LDAP_PASSWORD_QRCODE_DTO = {
    **BASE_DTO | {
        'userType': 'LDAP',
        'authnTypes': ['password', 'qrcode'],
        'userConfig': {'user': {'userType': 'LDAP'}},
        'qrcodeResponse': '123456',
        'qrcodeTransactionId': '3ec6abed-633c-4fa8-9613-418224bb6025'
    }
}

LDAP_PASSWORD_OTP_DTO = {
    **BASE_DTO | {
        'userType': 'LDAP',
        'authnTypes': ['password', 'otp'],
        'userConfig': {'user': {'userType': 'LDAP'}},
        'otp': '098765'
    }
}

LDAP_PASSWORD_AUTHN_CODE_DTO = {
    **BASE_DTO | {
        'userType': 'LDAP',
        'authnTypes': ['password', 'authncode'],
        'userConfig': {'user': {'userType': 'LDAP'}},
        'forgotTokenAuthnCode': '111765',
        'forgotTokenRandomChallenge': '234567'
    }
}

# KWARGS
PASSWORD_REQUESTED_KWARGS = {
    'Message': '{"type": "PASSWORD_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AUTH_POINT", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password"], '
               '"password": "strong-password#01"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'PASSWORD_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AUTH_POINT'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-topic.fifo'
}

PUSH_REQUESTED_KWARGS = {
    'Message': '{"type": "PUSH_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AUTH_POINT", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "sourceType": 2, "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["push"]}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'PUSH_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AUTH_POINT'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-topic.fifo'
}

OTP_REQUESTED_KWARGS = {
    'Message': '{"type": "OTP_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AUTH_POINT", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["otp"], '
               '"otp": "098765"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'OTP_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AUTH_POINT'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-topic.fifo'
}

PASSKEY_REQUESTED_KWARGS = {
    'Message': '{"type": "PASSKEY_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AUTH_POINT", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["passkey"], '
               '"passkeyTransactionId": "111-111", '
               '"passkey": {"id": "VmZ2kDoJXaDLbXL17G5Dqw"}}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'PASSKEY_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AUTH_POINT'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-topic.fifo'
}

QRCODE_REQUESTED_KWARGS = {
    'Message': '{"type": "QRCODE_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AUTH_POINT", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "sourceType": 2, "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["qrcode"], '
               '"qrcodeResponse": "123456", '
               '"qrcodeTransactionId": '
               '"3ec6abed-633c-4fa8-9613-418224bb6025"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'QRCODE_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AUTH_POINT'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-topic.fifo'
}

PASSWORD_PUSH_REQUESTED_KWARGS = {
    'Message': '{"type": "PASSWORD_PUSH_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AUTH_POINT", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "sourceType": 2, "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password", "push"], '
               '"password": "strong-password#01"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'PASSWORD_PUSH_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AUTH_POINT'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-topic.fifo'
}

PASSWORD_OTP_REQUESTED_KWARGS = {
    'Message': '{"type": "PASSWORD_OTP_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AUTH_POINT", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password", "otp"], '
               '"password": "strong-password#01", "otp": "098765"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'PASSWORD_OTP_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AUTH_POINT'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-topic.fifo'
}

PASSWORD_QRCODE_REQUESTED_KWARGS = {
    'Message': '{"type": "PASSWORD_QRCODE_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AUTH_POINT", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "sourceType": 2, "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password", "qrcode"], "qrcodeResponse": "123456", '
               '"qrcodeTransactionId": '
               '"3ec6abed-633c-4fa8-9613-418224bb6025", '
               '"password": "strong-password#01"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'PASSWORD_QRCODE_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AUTH_POINT'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-topic.fifo'
}

PASSWORD_AUTHN_CODE_REQUESTED_KWARGS = {
    'Message': '{"type": "PASSWORD_AUTHN_CODE_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AUTH_POINT", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password", "authncode"], '
               '"password": "strong-password#01", '
               '"forgotTokenAuthnCode": "111765", '
               '"forgotTokenRandomChallenge": '
               '"234567"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'PASSWORD_AUTHN_CODE_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AUTH_POINT'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-topic.fifo'
}

AUTHN_CODE_REQUESTED_KWARGS = {
    'Message': '{"type": "AUTHN_CODE_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AUTH_POINT", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["authncode"], '
               '"forgotTokenAuthnCode": "111765", '
               '"forgotTokenRandomChallenge": '
               '"234567"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'AUTHN_CODE_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AUTH_POINT'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-topic.fifo'
}

AZURE_AD_PASSWORD_REQUESTED_KWARGS = {
    'Message': '{"type": "AZURE_AD_PASSWORD_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AZURE_AD", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password"], '
               '"password": "strong-password#01"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'AZURE_AD_PASSWORD_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AZURE_AD'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-pw-azure-ad-topic.fifo'
}

AZURE_AD_PASSWORD_PUSH_REQUESTED_KWARGS = {
    'Message': '{"type": "AZURE_AD_PASSWORD_PUSH_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AZURE_AD", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "sourceType": 2, "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password", "push"], '
               '"password": "strong-password#01"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'AZURE_AD_PASSWORD_PUSH_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AZURE_AD'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-pw-azure-ad-topic.fifo'
}

AZURE_AD_PASSWORD_OTP_REQUESTED_KWARGS = {
    'Message': '{"type": "AZURE_AD_PASSWORD_OTP_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AZURE_AD", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password", "otp"], '
               '"password": "strong-password#01", "otp": "098765"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'AZURE_AD_PASSWORD_OTP_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AZURE_AD'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-pw-azure-ad-topic.fifo'
}

AZURE_AD_PASSWORD_QRCODE_REQUESTED_KWARGS = {
    'Message': '{"type": "AZURE_AD_PASSWORD_QRCODE_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AZURE_AD", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "sourceType": 2, "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password", "qrcode"], "qrcodeResponse": "123456", '
               '"qrcodeTransactionId": '
               '"3ec6abed-633c-4fa8-9613-418224bb6025", '
               '"password": "strong-password#01"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'AZURE_AD_PASSWORD_QRCODE_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AZURE_AD'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-pw-azure-ad-topic.fifo'
}

AZURE_AD_PASSWORD_AUTHN_CODE_REQUESTED_KWARGS = {
    'Message': '{"type": "AZURE_AD_PASSWORD_AUTHN_CODE_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "AZURE_AD", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password", "authncode"], '
               '"password": "strong-password#01", '
               '"forgotTokenAuthnCode": "111765", '
               '"forgotTokenRandomChallenge": '
               '"234567"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'AZURE_AD_PASSWORD_AUTHN_CODE_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'AZURE_AD'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-pw-azure-ad-topic.fifo'
}

LDAP_PASSWORD_REQUESTED_KWARGS = {
    'Message': '{"type": "LDAP_PASSWORD_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "LDAP", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password"], '
               '"password": "strong-password#01"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'LDAP_PASSWORD_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'LDAP'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-pw-ldap-topic.fifo'
}

LDAP_PASSWORD_PUSH_REQUESTED_KWARGS = {
    'Message': '{"type": "LDAP_PASSWORD_PUSH_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "LDAP", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "sourceType": 2, "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password", "push"], '
               '"password": "strong-password#01"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'LDAP_PASSWORD_PUSH_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'LDAP'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-pw-ldap-topic.fifo'
}

LDAP_PASSWORD_OTP_REQUESTED_KWARGS = {
    'Message': '{"type": "LDAP_PASSWORD_OTP_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "LDAP", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password", "otp"], '
               '"password": "strong-password#01", "otp": "098765"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'LDAP_PASSWORD_OTP_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'LDAP'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-pw-ldap-topic.fifo'
}

LDAP_PASSWORD_QRCODE_REQUESTED_KWARGS = {
    'Message': '{"type": "LDAP_PASSWORD_QRCODE_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "LDAP", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "sourceType": 2, "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password", "qrcode"], "qrcodeResponse": "123456", '
               '"qrcodeTransactionId": '
               '"3ec6abed-633c-4fa8-9613-418224bb6025", '
               '"password": "strong-password#01"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'LDAP_PASSWORD_QRCODE_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'LDAP'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-pw-ldap-topic.fifo'
}

LDAP_PASSWORD_AUTHN_CODE_REQUESTED_KWARGS = {
    'Message': '{"type": "LDAP_PASSWORD_AUTHN_CODE_REQUESTED", '
               '"entityType": "OIDC_AUTHENTICATION", '
               '"source": "flk-oidc-authn-api", '
               '"timestamp": 1632960000000, "data": '
               '{"accountId": "WGC-0", "chainId": "b09165ce-9afe-4585-8ccd-f1a08c25555a", "userId": 12, '
               '"transactionId": "txid12345", '
               '"userType": "LDAP", "loginType": '
               '"EMAIL", "login": "johndoe", '
               '"sourceIp": "0.0.0.0", "resourceName": "aaaa", "os": "Windows", "browser": '
               '"Firefox", "city": "Santa Rita do '
               'Sapucai", "regionName": "Minas '
               'Gerais", "authnTypes": ["password", "authncode"], '
               '"password": "strong-password#01", '
               '"forgotTokenAuthnCode": "111765", '
               '"forgotTokenRandomChallenge": '
               '"234567"}, '
               '"accountId": "WGC-0", "entityId": 12}',
    'MessageAttributes': {'entityType': {'DataType': 'String',
                                         'StringValue': 'OIDC_AUTHENTICATION'},
                          'eventType': {'DataType': 'String',
                                        'StringValue': 'LDAP_PASSWORD_AUTHN_CODE_REQUESTED'},
                          'userType': {'DataType': 'String',
                                       'StringValue': 'LDAP'}},
    'MessageGroupId': 'WGC-0#USER#12',
    'TopicArn': 'flk-authn-core-request-pw-ldap-topic.fifo'
}
