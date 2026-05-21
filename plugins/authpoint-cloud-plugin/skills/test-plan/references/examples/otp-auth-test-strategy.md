# M1 - Authentication of Azure/Local users using OTP - Test Strategy

## Test Strategies

### General Guidelines

- Focus on users experiences and typical scenarios
- Functional testing

---

## Test Plan

### Stories

[AAAS-21758](https://watchguard.atlassian.net/browse/AAAS-21758)

[AAAS-21283](https://watchguard.atlassian.net/browse/AAAS-21283)

---

## Test Scenario

[AAAS-21283](https://watchguard.atlassian.net/browse/AAAS-21283) - AuthPoint to authenticate platform oidc users with OTP without authentication policy

[AAAS-21696](https://watchguard.atlassian.net/browse/AAAS-21696)

| **Scenarios** | **Expected Behavior** | **Result** | **Notes** |
|---|---|---|---|
| Create a new Azure provider in AuthPoint 1.0 | Check in flk-cache-settings db if the register was created to this account | | |
| Update an Azure provider in AuthPoint 1.0 | Check in flk-cache-settings db if the register was updated to this account | | |
| Delete an Azure provider in AuthPoint 1.0 | Check in flk-cache-settings db if the register was deleted to this account | | |

[AAAS-21633](https://watchguard.atlassian.net/browse/AAAS-21633)

| **Scenarios** | **Expected Behavior** | **Result** | **Notes** |
|---|---|---|---|
| Add new mobile token to the user in AuthPoint 1.0 | Check in flk-core-credentials if the register was created to this user | | |
| Change token status from Active to Manually blocked in AuthPoint 1.0 | Check in flk-core-credentials if the register was updated to this user | | |
| Change token status from Manually blocked to Active in AuthPoint 1.0 | Check in flk-core-credentials if the register was updated to this user | | |
| Delete mobile token in AuthPoint 1.0 | Check in flk-core-credentials db if the register was deleted to this user | | |
| Add 2 software tokens for the same user. Remove only one user software token | Check in flk-core-credentials db if the register was deleted to this user | | |
| Add 5 software tokens for the same user. Remove all tokens in the same array | Check in flk-core-credentials db if the register was deleted to this user | | |
| Add 2 software tokens for the same user. In the array to make the deletion, pass the correct serial number and another wrong serial number | It should give an error | | |

[AAAS-21630](https://watchguard.atlassian.net/browse/AAAS-21630) / [AAAS-21705](https://watchguard.atlassian.net/browse/AAAS-21705)

| **Scenarios** | **Expected Behavior** | **Result** | **Notes** |
|---|---|---|---|
| An MFA local user provides the correct Password and the correct OTP. | Successfully authenticated | | |
| An MFA Azure user provides the correct Password and the correct OTP. | Successfully authenticated | | |
| A non-MFA user provides the correct Password. | Successfully authenticated | | |
| A non-MFA user provides the incorrect Password. | The authentication has been denied | | |
| A non-MFA user provides the incorrect Password. Up to the limit of attempts to block the user. | The authentication has been denied | | |
| The system allows users to enter the OTP within the specified timeout period. | Successfully authenticated | | |
| An MFA local user provides the correct Password, but the OTP is incorrect. | The authentication has been denied | | |
| An MFA local user provides the correct Password, but the OTP was used before. | The authentication has been denied | | |
| An MFA local user provides the correct Password, but the OTP field is empty. | The authentication has been denied | | |
| An MFA local user provides the correct Password, but in the OTP field uses letters instead of numbers. | The authentication has been denied | | |
| An MFA Azure user provides the correct Password, but the OTP was used before. | The authentication has been denied | | |
| An MFA Azure user provides the correct Password, but the OTP field is empty. | The authentication has been denied | | |
| An MFA Azure user provides the correct Password, but in the OTP field uses letters instead of numbers. | The authentication has been denied | | |
| An MFA local user provides the incorrect Password and the correct OTP. | The authentication has been denied | | |
| An MFA local user provides the incorrect Password and the correct OTP. Up to the limit of attempts to block the user. | The authentication has been denied | | |
| An MFA local user is manually locked out. | The authentication has been denied | | |
| An MFA Azure user provides the incorrect Password and the correct OTP. | The authentication has been denied | | |
| An MFA Azure user provides the correct Password and the incorrect OTP. Up to the limit of attempts to block the user. | The authentication has been denied | | |
| An MFA local user provides an incorrect OTP, but the token is blocked automatically. | The authentication has been denied | | |
| The system denies authentication if the user does not enter the OTP within the timeout period, regardless of whether it is correct. | The authentication has been denied | | |
