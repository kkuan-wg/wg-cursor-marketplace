# DTOs

VALID_DTO = {
    'accountId': 'WGC-0'
}

INVALID_DTO = {
    'accountId': 'W'
}

# DB ITEMS

CLIENT_DDB_ITEM_ID_TOKEN = {
    'partitionKey': 'WGC-0#OIDC_CLIENT#123-abc',
    'accountId': 'WGC-0',
    'resourceId': 123,
    'lastUpdatedOn': 1582815816,
    'friendlyType': 'WG_INTERNAL',
    'applicationType': 'FIREWAN',
    'responseType': 'id_token',
    'redirectUris': ['example.com/callback', 'example.com/other_callback'],
    'clientId': '123-abc',
    'clientName': 'Client Name',
    'issuer': 'oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0',
    'clientSecret': 'client_secret',
    'customClaims': [{'name': 'preferred_username', 'value': 'username'}, {'name': 'groups', 'value': 'groups'}]
}

CLIENT_DDB_ITEM_CODE = {
    'partitionKey': 'WGC-0#OIDC_CLIENT#123-abc',
    'accountId': 'WGC-0',
    'resourceId': 123,
    'lastUpdatedOn': 1582815816,
    'friendlyType': 'WG_INTERNAL',
    'applicationType': 'FIREWAN',
    'responseType': 'code',
    'redirectUris': ['example.com/callback', 'example.com/other_callback'],
    'clientId': '123-abc',
    'clientName': 'Client Name',
    'issuer': 'oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0',
    'clientSecret': 'client_secret',
    'customClaims': [{'name': 'preferred_username', 'value': 'username'}, {'name': 'groups', 'value': 'groups'}]
}

# RESPONSES

SUCCESS_RESPONSE_ID_TOKEN = {
    'body':
        '{"issuer": "oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0", '
        '"authorization_endpoint": "oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0/authorize", '
        '"jwks_uri": "oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0/cert", '
        '"userinfo_endpoint": "oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0/userinfo", '
        '"scopes_supported": ["openid", "email", "profile"], '
        '"response_types_supported": ["id_token"], '
        '"subject_types_supported": ["public"], '
        '"id_token_signing_alg_values_supported": ["RS256"], '
        '"claim_types_supported": ["normal"]}',
    'headers': {'Access-Control-Allow-Credentials': True,
                'Access-Control-Allow-Origin': None,
                'Access-Control-Expose-Headers': 'Request-Id',
                'Content-Type': 'application/json'},
    'statusCode': 200
}

SUCCESS_RESPONSE_CODE = {
    'body':
        '{"issuer": '
        '"oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0", '
        '"authorization_endpoint": "oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0/authorize", '
        '"jwks_uri": "oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0/cert", '
        '"userinfo_endpoint": "oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0/userinfo", '
        '"scopes_supported": ["openid", "email", "profile"], '
        '"response_types_supported": ["code"], '
        '"subject_types_supported": ["public"], '
        '"id_token_signing_alg_values_supported": ["RS256"], '
        '"claim_types_supported": ["normal"], '
        '"token_endpoint": "oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0/token", '
        '"token_endpoint_auth_methods_supported": ["client_secret_basic"]}',
    'headers': {'Access-Control-Allow-Credentials': True,
                'Access-Control-Allow-Origin': None,
                'Access-Control-Expose-Headers': 'Request-Id',
                'Content-Type': 'application/json'},
    'statusCode': 200
}

SUCCESS_RESPONSE_CODE_ID_TOKEN = {
    'body':
        '{"issuer": "oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0", '
        '"authorization_endpoint": "oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0/authorize", '
        '"jwks_uri": "oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0/cert", '
        '"userinfo_endpoint": "oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0/userinfo", '
        '"scopes_supported": ["openid", "email", "profile"], '
        '"response_types_supported": ["code", "id_token"], '
        '"subject_types_supported": ["public"], '
        '"id_token_signing_alg_values_supported": ["RS256"], '
        '"claim_types_supported": ["normal"],'
        ' "token_endpoint": "oidc.authpoint.amer.ha.cloud.watchguard.com/authx/account/WGC-0/token", '
        '"token_endpoint_auth_methods_supported": ["client_secret_basic"]}',
    'headers': {'Access-Control-Allow-Credentials': True,
                'Access-Control-Allow-Origin': None,
                'Access-Control-Expose-Headers': 'Request-Id',
                'Content-Type': 'application/json'},
    'statusCode': 200
}

# ERROR RESPONSES

NO_OIDC_CLIENTS_ERR_RESP = {
    'body': '{"error": "invalid_request", "error_description": "There are no oidc '
            'clients for this account"}',
    'headers': {'Access-Control-Allow-Credentials': True,
                'Access-Control-Allow-Origin': None,
                'Access-Control-Expose-Headers': 'Request-Id',
                'Content-Type': 'application/json'},
    'statusCode': 400
}

INVALID_ACCOUNT_ID_ERR_RESP = {
    'body': '{"error": "invalid_request", "error_description": "The request is '
            'missing the accountId parameter or it has an invalid value"}',
    'headers': {'Access-Control-Allow-Credentials': True,
                'Access-Control-Allow-Origin': None,
                'Access-Control-Expose-Headers': 'Request-Id',
                'Content-Type': 'application/json'},
    'statusCode': 400
}

# REQUIRED_FIELDS

REQUIRED_FIELDS = {'accountId': {'type': str, 'minLength': 5}}
