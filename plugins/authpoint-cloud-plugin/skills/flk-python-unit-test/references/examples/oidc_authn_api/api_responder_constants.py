REQUEST_ID = '123'

# DTOs
VALID_DTO = {
    'accountId': 'WGC-0',
    'login': 'luffy',
    'httpMethod': 'POST',
    'extendedRequestId': '123',
    'requestId': '123',
    'authnTypes': ['password'],
    'transactionId': 'tx-123-abc'
}

ACCEPTED_DTO = {
    **VALID_DTO,
    'transactionId': 'tx-123-abc'
}

# SUCCESS RESPONSES

SUCCESS_ACCEPTED_RESPONSE = {
    'body': '{"transactionId": "tx-123-abc"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 202
}

# ERROR RESPONSES

INVALID_ACCOUNT_ID_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The request body is missing '
            'the accountId parameter or it has an invalid value", "status": 400, '
            '"code": "601003001"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 400
}

INVALID_LOGIN_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The request body is missing '
            'the username parameter or it has an invalid value", "status": 400, '
            '"code": "601003002"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 400
}

INVALID_PASSWORD_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The request body is missing '
            'the password parameter or it has an invalid value", "status": 400, '
            '"code": "601003003"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 400
}

INVALID_OTP_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The request body is missing '
            'the otp parameter or it has an invalid value", "status": 400, '
            '"code": "601003004"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 400
}

INVALID_QRCODE_RESPONSE_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The request body is missing '
            'the qrcodeResponse parameter or it has an invalid value", "status": 400, '
            '"code": "601003005"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 400
}

INVALID_QRCODE_TRANSACTION_ID_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The request body is missing '
            'the qrcodeTransactionId parameter or it has an invalid value", "status": 400, '
            '"code": "601003006"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 400
}

INVALID_FORGOT_TOKEN_AUTHN_CODE_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The request body is missing '
            'the forgotTokenAuthnCode parameter or it has an invalid value", "status": 400, '
            '"code": "601003007"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 400
}

INVALID_COOKIE_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The request is missing '
            'the cookieHeader or it has an invalid value", "status": 400, '
            '"code": "601003008"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 400
}

AUTHN_CONTEXT_EXPIRED_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The Authn Context entity for '
            'the authpoint_sso_context was not found or is expired", "status": 401, '
            '"code": "601003009"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 401
}

INVALID_REQUEST_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The request is missing '
            'a required parameter or it has an invalid value", "status": 400, '
            '"code": "601003010"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 400
}

INVALID_ACCURACY_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The request is missing '
            'the accuracy parameter or it has an invalid value", "status": 400, '
            '"code": "601003011"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 400
}

INVALID_LATITUDE_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The request is missing '
            'the latitude parameter or it has an invalid value", "status": 400, '
            '"code": "601003012"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 400
}

INVALID_LONGITUDE_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The request is missing '
            'the longitude parameter or it has an invalid value", "status": 400, '
            '"code": "601003013"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 400
}

INVALID_APPLICATION_TYPE_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The applicationType parameter '
            'has an invalid value", "status": 400, '
            '"code": "601003014"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 400
}

INVALID_AUTHN_TYPES_RESPONSE = {
    'body': '{"title": "invalid_request", "detail": "The request body is missing '
            'the authnTypes parameter or it has an invalid value", "status": 400, '
            '"code": "601003015"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 400
}

INTERNAL_SERVER_ERROR_RESPONSE = {
    'body': '{"title": "server_error", "detail": "An unexpected server error '
            'occurred", "status": 500, "code": "601003301"}',
    'headers': {
        'Access-Control-Allow-Credentials': True,
        'Access-Control-Allow-Origin': None,
        'Content-Type': 'application/json',
        'Request-Id': REQUEST_ID,
        'Access-Control-Expose-Headers': 'Request-Id'
    },
    'statusCode': 500
}
