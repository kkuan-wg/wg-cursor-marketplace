AUTHN_CONTEXT_ID = 'e761cb08-bf00-475f-992a-11ae2ac488f1'
REQUEST_ID = '123'
COOKIE = (r'_rollupGa=GA1.2.701387687.1683555256; x=y; '
          r'authpoint_sso_context=eyJhdXRobkNvbnRleHRJZCI6ICJlNzYxY2IwOC1iZjAwLTQ3NWYtOTkyYS0xMWFlMmFjNDg4Z'
          r'jEiLCAiY2xpZW50SWQiOiAiMDg5NTM2ZjktYjQ4ZS00YjIyLTlmMjItYTcxMTQ5NTQzYmQzIn0=; '
          r'Path=/; Secure; HttpOnly;')

# API RESPONSES

API_RESPONSE_WITH_SUCCESS = {
    'status': 200,
    'body': [
        {
            'allowAuth': True,
            'policy': {
                'otp': False,
                'push': False,
                'qrcode': False,
                'passkey': False,
                'password': True
            },
            'name': 'Main Policy'
        }
    ]
}

API_RESPONSE_WITH_ERROR = {
    'status': 500,
    'body': {
        "status": "failed",
        "error": "1 validation error for ClientInfoRequest\nuser_id\n  Field required [type=missing, input_value={'user_ids': '1000464', '...1-bbfc0861703e4c7193aa'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.6/v/missing"
    }
}

BASE_EXPECTED_REQUEST = {
    'headers': {'content-type': 'application/json'},
    'method': 'POST',
    'params': {},
    'url': 'zte-policy-evaluator/v1/WGC-0/evaluate'
}

EXPECTED_REQUEST = {
    **BASE_EXPECTED_REQUEST,
    'data': b'{"user_id": "121", "namespace": "AUTHPOINT", "ip_address": "1.0.0.1", "groups": '
            b'[{"id": "71"}], "resources": [{"id": "123"}]}'
}

EXPECTED_REQUEST_WITHOUT_ELIGIBLE_GROUPS = {
    **BASE_EXPECTED_REQUEST,
    'data': b'{"user_id": "121", "namespace": "AUTHPOINT", "ip_address": "1.0.0.1", "groups": '
            b'[{"id": "71"}, {"id": "456"}], "resources": [{"id": "123"}]}'
}

EXPECTED_REQUEST_WITH_GEOLOCATION = {
    **BASE_EXPECTED_REQUEST,
    'data': b'{"user_id": "121", "namespace": "AUTHPOINT", "accuracy": 11.71, "latitude": -22.4451083, '
            b'"longitude": -45.4551853, "ip_address": "1.0.0.1", "groups": [{"id": "71"}], '
            b'"resources": [{"id": "123"}]}'
}

EXPECTED_REQUEST_WITH_PREVIOUS_LOCATION = {
    **BASE_EXPECTED_REQUEST,
    'data': b'{"user_id": "121", "namespace": "AUTHPOINT", "ip_address": "1.0.0.1", "groups": [{"id": "71"}], '
            b'"resources": [{"id": "123"}], "previous_location": {"latitude": -22.0, "longitude": -45.0, '
            b'"timestamp": 1751639268000}}'
}

EXPECTED_RESPONSE = {
    'allowAuth': True,
    'policy': {
        'otp': False,
        'push': False,
        'qrcode': False,
        'passkey': False,
        'password': True
    },
    'name': 'Main Policy'
}

PARSED_RESPONSE = {
    'status': 200,
    'body': [
        EXPECTED_RESPONSE
    ]
}

ZTE_RESPONSE_WITH_SUCCESS = {
    'status': 200,
    'body': [
        {
            "action_type": "AUTHENTICATION",
            "action": "ALLOWED",
            "authentication_type": {
                "qr": False,
                "password": True,
                'passkey': False,
                "otp": False,
                "push": False
            },
            'name': 'Main Policy'
        }
    ]
}
