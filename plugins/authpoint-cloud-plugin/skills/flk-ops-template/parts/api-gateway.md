# API Gateway

---

## Globals.Api block

Always include in sub-stacks that expose an API:

```yaml
Globals:
  Api:
    OpenApiVersion: "3.0.3"
    AlwaysDeploy: True
    MethodSettings:
      - HttpMethod: "*"
        ResourcePath: "/*"
        LoggingLevel: !Ref ApiGatewayLoggingLevel   # Parameter: INFO or ERROR
        DataTraceEnabled: false                     # Never log request/response body
```

> `DataTraceEnabled: false` is mandatory — it prevents sensitive data from appearing in CloudWatch logs.

---

## AWS::Serverless::Api resource

```yaml
LogonAppAuthAPI:
  Type: AWS::Serverless::Api
  Properties:
    Name: !Sub '${StackModifier}-logon-app-auth-api'
    StageName: !Ref Environment
    TracingEnabled: False
    Cors:
      AllowCredentials: true
      AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
      AllowHeaders: "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
      AllowOrigin: !Sub "'${WGCAllowedOrigin}'"
    DefinitionBody:
      Fn::Transform:
        Name: AWS::Include
        Parameters:
          Location: swagger.yaml
    Tags:
      wg:info:taggingversion: 2.1.0
      wg:purpose:product: authpoint
      wg:purpose:serviceid: folklore-service-logon-app
      wg:purpose:environment: !Ref Environment
      wg:purpose:region: !Ref AWS::Region
      wg:automation:expiry: never
      wg:compliance:program: pci
      wg:compliance:dataclassification: business-only
      wg:compliance:specialdata: customerorigin
      wg:info:owner: authpoint
```

> `TracingEnabled: False` is mandatory — X-Ray tracing is disabled across all Folklore services.

**Parameters used only in Swagger:** when `DefinitionBody` pulls in `swagger.yaml` via `AWS::Include`, CloudFormation parameters may be referenced **only** in that file. See [template-validation.md](template-validation.md).

---

## WAF association

Attach a WAF WebACL to the API stage after deployment:

```yaml
LogonAppAuthAPIWAFAssociation:
  Type: AWS::WAFv2::WebACLAssociation
  DependsOn: LogonAppAuthAPIStage   # SAM generates stage as <ApiName>Stage
  Properties:
    ResourceArn: !Sub
      - 'arn:aws:apigateway:${AWS::Region}::/restapis/${ApiId}/stages/${Environment}'
      - ApiId: !Ref LogonAppAuthAPI
    WebACLArn: !Ref WAFWebACLArn    # Passed as Parameter from root template
```

> The `DependsOn` must reference the SAM-generated stage resource name: `<ApiLogicalId>Stage`.

---

## IAM Role for API Gateway CloudWatch logging

Required once per account/region — typically in the API sub-stack:

```yaml
ApiGatewayCloudWatchRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: !Sub '${StackModifier}-api-gw-cloudwatch-role'
    AssumeRolePolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Principal:
            Service: apigateway.amazonaws.com
          Action: sts:AssumeRole
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs

ApiGatewayAccount:
  Type: AWS::ApiGateway::Account
  Properties:
    CloudWatchRoleArn: !GetAtt ApiGatewayCloudWatchRole.Arn
```

---

## Lambda API trigger

On the Lambda function, reference the API resource:

```yaml
FlkLogonAppConfigApiFn:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName: !Sub '${StackModifier}-flk-logon-app-config-api'
    CodeUri: flk_logon_app_config_api/
    Description: Handles config API requests
    ReservedConcurrentExecutions: !FindInMap [ ReservedConcurrentExecutions, !Ref Environment, concurrency ]
    Policies:
      - DynamoDBReadPolicy:
          TableName: !Ref FlkLogonAppConfigTable
    Events:
      GetConfig:
        Type: Api
        Properties:
          RestApiId: !Ref LogonAppAuthAPI
          Path: /config
          Method: GET
      PostConfig:
        Type: Api
        Properties:
          RestApiId: !Ref LogonAppAuthAPI
          Path: /config
          Method: POST
```

---

## Swagger file pattern

The `DefinitionBody` references a `swagger.yaml` file co-located with the template. The Swagger file uses API Gateway extensions to wire Lambda integrations:

```yaml
# swagger.yaml (excerpt)
paths:
  /config:
    get:
      x-amazon-apigateway-integration:
        uri:
          Fn::Sub: 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${FlkLogonAppConfigApiFn.Arn}/invocations'
        httpMethod: POST
        type: aws_proxy
```

---

## Outputs

Export the API URL and ID for cross-stack references:

```yaml
Outputs:
  LogonAppAuthAPIUrl:
    Description: API Gateway URL
    Value: !Sub 'https://${LogonAppAuthAPI}.execute-api.${AWS::Region}.amazonaws.com/${Environment}'
    Export:
      Name: !Sub '${StackModifier}-logon-app-auth-api-url'

  LogonAppAuthAPIId:
    Description: API Gateway ID
    Value: !Ref LogonAppAuthAPI
    Export:
      Name: !Sub '${StackModifier}-logon-app-auth-api-id'
```

---

## Checklist

- [ ] OpenAPI/Swagger cross-checked for parameter usage and valid `!Sub` / resource refs (see [template-validation.md](template-validation.md))
- [ ] `TracingEnabled: False` on `AWS::Serverless::Api`
- [ ] `DataTraceEnabled: false` in `Globals.Api.MethodSettings`
- [ ] CORS configured with `AllowCredentials`, `AllowMethods`, `AllowHeaders`, `AllowOrigin`
- [ ] `DefinitionBody` uses `Fn::Transform` / `AWS::Include` pointing to `swagger.yaml`
- [ ] `AWS::WAFv2::WebACLAssociation` with `DependsOn: <ApiName>Stage`
- [ ] `AWS::IAM::Role` + `AWS::ApiGateway::Account` for CloudWatch logs
- [ ] Lambda `Events` reference `RestApiId: !Ref <ApiResource>`
- [ ] API URL and ID exported in `Outputs`
