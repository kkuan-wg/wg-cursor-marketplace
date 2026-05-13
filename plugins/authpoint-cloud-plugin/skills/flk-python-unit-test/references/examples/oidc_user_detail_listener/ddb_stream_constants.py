USER_SOFT_DELETED_EVENT = {
    'Records': [
        {
            'eventID': 'b8cbcd87a0bd77c7948b86a7b79dff58',
            'eventName': 'MODIFY', 'eventVersion': '1.1',
            'eventSource': 'aws:dynamodb',
            'awsRegion': 'us-west-2',
            'dynamodb': {
                'ApproximateCreationDateTime': 1695650899.0,
                'Keys': {
                    'sortKey': {
                        'S': 'WGC-123456789#USER#123'
                    }
                },
                'NewImage': {'lastName': {'S': 'monkey d.'},
                             'accessProperties': {'L': [
                                 {
                                     'M': {
                                         'originUserId': {'S': 'origin-user-id'},
                                         'originAccountId': {'S': 'origin-account-id'},
                                         'type': {'S': 'VISITOR_REPLICA'}
                                     }
                                 },
                                 {
                                     'M': {
                                         'type': {'S': 'VISITOR_ORIGIN'}
                                     }
                                 },
                                 {
                                     'M': {
                                         'name': {'S': 'trepidatious_administrators'},
                                         'type': {'S': 'ALIAS_PARTY'},
                                         'users': {
                                             'L': [
                                                 {'N': '123'},
                                                 {'N': '456'}]
                                         }
                                     }
                                 },
                                 {
                                     'M': {
                                         'type': {'S': 'ALIAS_MEMBER'}
                                     }
                                 }]},
                             'userId': {'N': '123'},
                             'type': {'S': 'AUTH_POINT'},
                             'usernameGsi': {'S': 'WGC-123456789#luffy'},
                             'groupsIds': {'L': [{'N': '71'},
                                                 {'N': '72'},
                                                 {'N': '73'}]
                                           },
                             'accountId': {'S': 'WGC-123456789'},
                             'firstName': {'S': 'luffy'},
                             'isAuthenticationAllowed': {'BOOL': True},
                             'sortKey': {'S': 'WGC-123456789#USER#123'},
                             'overAllocated': {'BOOL': False},
                             'lastUpdatedOn': {'N': '1582815816'},
                             'quarantine': {'BOOL': False},
                             'isMfa': {'BOOL': False},
                             'emailGsi': {'S': 'WGC-123456789#luffy@email.com'},
                             'visitor': {'BOOL': True},
                             'softDeletedTtl': {'N': '1663167600'},
                             'email': {'S': 'luffy@email.com'},
                             'status': {'S': 'BLOCKED'},
                             'username': {'S': 'luffy'}
                             },
                'OldImage': {'lastName': {'S': 'monkey d.'},
                             'accessProperties': {'L': [{
                                 'M': {
                                     'originUserId': {'S': 'origin-user-id'},
                                     'originAccountId': {'S': 'origin-account-id'},
                                     'type': {'S': 'VISITOR_REPLICA'}}},
                                 {
                                     'M': {
                                         'type': {'S': 'VISITOR_ORIGIN'}}},
                                 {
                                     'M': {
                                         'name': {'S': 'trepidatious_administrators'},
                                         'type': {'S': 'ALIAS_PARTY'},
                                         'users': {
                                             'L': [
                                                 {'N': '123'},
                                                 {'N': '456'}]}}},
                                 {
                                     'M': {
                                         'type': {'S': 'ALIAS_MEMBER'}}}]},
                             'userId': {'N': '123'},
                             'type': {'S': 'AUTH_POINT'},
                             'usernameGsi': {'S': 'WGC-123456789#luffy'},
                             'groupsIds': {'L': [{'N': '71'},
                                                 {'N': '72'}]},
                             'accountId': {
                                 'S': 'WGC-123456789'},
                             'firstName': {'S': 'luffy'},
                             'isAuthenticationAllowed': {
                                 'BOOL': True},
                             'sortKey': {'S': 'WGC-123456789#USER#123'},
                             'overAllocated': {'BOOL': False},
                             'lastUpdatedOn': {'N': '1582815816'},
                             'quarantine': {'BOOL': False},
                             'isMfa': {'BOOL': False},
                             'emailGsi': {'S': 'WGC-123456789#luffy@email.com'},
                             'visitor': {'BOOL': True},
                             'softDeletedTtl': {'N': '0'},
                             'email': {'S': 'luffy@email.com'},
                             'status': {'S': 'BLOCKED'},
                             'username': {'S': 'luffy'}},
                'SequenceNumber': '551579100000000021955289680',
                'SizeBytes': 1228,
                'StreamViewType': 'NEW_AND_OLD_IMAGES'},
            'eventSourceARN': 'arn:aws:dynamodb:us-west-2:271161384030:table/dev-global-flk-oidc-user-detail/'
                              'stream/2023-06-01T16:24:12.001'
        }
    ]
}

USER_BLOCKED_EVENT = {
    'Records': [
        {
            'eventID': '6bb4d779914f7d7cc3e449597da5017c',
            'eventName': 'MODIFY', 'eventVersion': '1.1',
            'eventSource': 'aws:dynamodb',
            'awsRegion': 'us-west-2',
            'dynamodb': {
                'ApproximateCreationDateTime': 1695650899.0,
                'Keys': {
                    'sortKey': {'S': 'WGC-123456789#USER#123'}
                },
                'NewImage': {'lastName': {'S': 'monkey d.'},
                             'accessProperties': {'L': [{
                                 'M': {
                                     'originUserId': {'S': 'origin-user-id'},
                                     'originAccountId': {'S': 'origin-account-id'},
                                     'type': {'S': 'VISITOR_REPLICA'}}},
                                 {
                                     'M': {
                                         'type': {'S': 'VISITOR_ORIGIN'}}},
                                 {
                                     'M': {
                                         'name': {'S': 'trepidatious_administrators'},
                                         'type': {'S': 'ALIAS_PARTY'},
                                         'users': {
                                             'L': [
                                                 {'N': '123'},
                                                 {'N': '456'}]}}},
                                 {
                                     'M': {
                                         'type': {'S': 'ALIAS_MEMBER'}}}]},
                             'userId': {'N': '123'},
                             'type': {'S': 'AUTH_POINT'},
                             'usernameGsi': {'S': 'WGC-123456789#luffy'},
                             'groupsIds': {'L': [{'N': '71'},
                                                 {'N': '72'},
                                                 {'N': '73'}]},
                             'accountId': {'S': 'WGC-123456789'},
                             'firstName': {'S': 'luffy'},
                             'isAuthenticationAllowed': {'BOOL': False},
                             'sortKey': {'S': 'WGC-123456789#USER#123'},
                             'overAllocated': {'BOOL': False},
                             'lastUpdatedOn': {'N': '1582815816'},
                             'quarantine': {'BOOL': False},
                             'isMfa': {'BOOL': True},
                             'emailGsi': {'S': 'WGC-123456789#luffy@email.com'},
                             'visitor': {'BOOL': True},
                             'softDeletedTtl': {'N': '0'},
                             'email': {'S': 'luffy@email.com'},
                             'status': {'S': 'BLOCKED'},
                             'username': {'S': 'luffy'}},
                'OldImage': {'lastName': {'S': 'monkey d.'},
                             'accessProperties': {'L': [{
                                 'M': {
                                     'originUserId': {'S': 'origin-user-id'},
                                     'originAccountId': {'S': 'origin-account-id'},
                                     'type': {'S': 'VISITOR_REPLICA'}}},
                                 {
                                     'M': {
                                         'type': {'S': 'VISITOR_ORIGIN'}}},
                                 {
                                     'M': {
                                         'name': {
                                             'S': 'trepidatious_administrators'},
                                         'type': {'S': 'ALIAS_PARTY'},
                                         'users': {
                                             'L': [
                                                 {'N': '123'},
                                                 {'N': '456'}]}}},
                                 {
                                     'M': {
                                         'type': {'S': 'ALIAS_MEMBER'}}}]},
                             'userId': {'N': '123'},
                             'type': {'S': 'AUTH_POINT'},
                             'usernameGsi': {'S': 'WGC-123456789#luffy'},
                             'groupsIds': {'L': [{'N': '71'},
                                                 {'N': '72'}]},
                             'accountId': {
                                 'S': 'WGC-123456789'},
                             'firstName': {'S': 'luffy'},
                             'isAuthenticationAllowed': {
                                 'BOOL': False},
                             'sortKey': {'S': 'WGC-123456789#USER#123'},
                             'overAllocated': {'BOOL': False},
                             'lastUpdatedOn': {'N': '1582815816'},
                             'quarantine': {'BOOL': False},
                             'isMfa': {'BOOL': True},
                             'emailGsi': {'S': 'WGC-123456789#luffy@email.com'},
                             'visitor': {'BOOL': True},
                             'softDeletedTtl': {'N': '0'},
                             'email': {'S': 'luffy@email.com'},
                             'status': {'S': 'BLOCKED'},
                             'username': {'S': 'luffy'}},
                'SequenceNumber': '551579100000000021955289680',
                'SizeBytes': 1228,
                'StreamViewType': 'NEW_AND_OLD_IMAGES'},
            'eventSourceARN': 'arn:aws:dynamodb:us-west-2:271161384030:table/dev-global-flk-oidc-user-detail/'
                              'stream/2023-06-01T16:24:12.001'
        }
    ]
}

USER_BLOCKED_DTO = {
    'eventType': 'MODIFY',
    'eventId': '6bb4d779914f7d7cc3e449597da5017c',
    'accountId': 'WGC-123456789',
    'userId': 123,
    'isAuthenticationAllowed': False,
    'groups': [71, 72, 73],
    'oldGroups': [71, 72],
    'isMfa': True,
    'oldIsMfa': True,
    'overAllocated': False,
    'quarantine': False,
    'status': 'BLOCKED',
    'softDeletedTtl': 0
}

USER_SOFT_DELETED_DTO = {
    'eventType': 'MODIFY',
    'eventId': 'b8cbcd87a0bd77c7948b86a7b79dff58',
    'accountId': 'WGC-123456789',
    'userId': 123,
    'isAuthenticationAllowed': True,
    'groups': [71, 72, 73],
    'oldGroups': [71, 72],
    'isMfa': False,
    'oldIsMfa': False,
    'overAllocated': False,
    'quarantine': False,
    'status': 'BLOCKED',
    'softDeletedTtl': 1663167600
}

USER_IS_MFA_CHANGED_DTO = {
    'eventType': 'MODIFY',
    'eventId': 'b8cbcd87a0bd77c7948b86a7b79df333',
    'accountId': 'WGC-123456789',
    'userId': 123,
    'isAuthenticationAllowed': True,
    'groups': [71, 72, 73],
    'oldGroups': [71, 72],
    'isMfa': True,
    'oldIsMfa': False,
    'overAllocated': False,
    'quarantine': False,
    'status': 'ACTIVE',
    'softDeletedTtl': 0
}

USER_GROUP_CHANGED_DTO = {
    'eventType': 'MODIFY',
    'eventId': 'b8cbcd87a0bd77c7948b86a7b79df666',
    'accountId': 'WGC-123456789',
    'userId': 123,
    'isAuthenticationAllowed': True,
    'groups': [71, 72],
    'oldGroups': [71, 72, 73],
    'isMfa': False,
    'oldIsMfa': False,
    'overAllocated': False,
    'quarantine': False,
    'status': 'ACTIVE',
    'softDeletedTtl': 0
}

USER_WITH_NO_GROUP_CHANGES_AND_NO_TERMINATION_CONDITIONS_DTO = {
    'eventType': 'MODIFY',
    'eventId': 'b8cbcd87a0bd77c7948b86a7b79df666',
    'accountId': 'WGC-123456789',
    'userId': 123,
    'isAuthenticationAllowed': True,
    'groups': [71, 72, 73],
    'oldGroups': [71, 72, 73],
    'isMfa': False,
    'oldIsMfa': False,
    'overAllocated': False,
    'quarantine': False,
    'status': 'ACTIVE',
    'softDeletedTtl': 0
}
