# Encryption at-rest (beyond SQS and SNS)

SQS and SNS are covered in [sqs.md](sqs.md) and [sns.md](sns.md). When templates define **other data stores**, enable encryption at-rest as below.

---

## Quick reference

SQS and SNS are covered in [sqs.md](sqs.md) and [sns.md](sns.md) — do not use this file for those.

| Resource type | Property | Typical value |
|---------------|----------|----------------|
| **Secrets Manager** | `KmsKeyId` | CMK id/ARN (required) |
| **S3** | `BucketEncryption` | `SSEAlgorithm: AES256` or `aws:kms` + optional `KMSMasterKeyID` |
| **DynamoDB** | `SSESpecification` | `SSEEnabled: true`; `SSEType: KMS` optional |
| **EFS** | `Encrypted` | `true`; `KmsKeyId` optional |
| **RDS** | `StorageEncrypted` | `true`; `KmsKeyId` optional |

---

## Examples (minimal)

**Secrets Manager**

```yaml
MySecret:
  Type: AWS::SecretsManager::Secret
  Properties:
    Name: !Sub '${StackModifier}-my-secret'
    KmsKeyId: !Ref MyKmsKeyId
```

**S3**

```yaml
MyBucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketName: !Sub '${StackModifier}-my-bucket'
    BucketEncryption:
      ServerSideEncryptionConfiguration:
        - ServerSideEncryptionByDefault:
            SSEAlgorithm: AES256
```

**DynamoDB**

```yaml
MyTable:
  Type: AWS::DynamoDB::Table
  Properties:
    TableName: !Ref MyTableName
    SSESpecification:
      SSEEnabled: true
```

**EFS**

```yaml
MyEfs:
  Type: AWS::EFS::FileSystem
  Properties:
    Encrypted: true
```

**RDS (instance or cluster)**

```yaml
MyDbInstance:
  Type: AWS::RDS::DBInstance
  Properties:
    StorageEncrypted: true
    # KmsKeyId: !Ref MyKmsKeyId   # optional: uses AWS managed key if omitted
```

---

## Checklist

- [ ] Every `AWS::SecretsManager::Secret` has `KmsKeyId`
- [ ] Every `AWS::S3::Bucket` has `BucketEncryption`
- [ ] Every `AWS::DynamoDB::Table` has `SSESpecification.SSEEnabled: true` when the table stores app data
- [ ] EFS/RDS used in the stack use encryption flags as required by compliance
