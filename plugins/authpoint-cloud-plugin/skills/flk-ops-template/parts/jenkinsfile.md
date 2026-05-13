# Jenkinsfile — `lambdaNames`

This part documents **only** how to define the list of deployed Lambda **function names** that the service must register (e.g. for monitoring or post-deploy hooks). **Pipeline implementation** (shared libraries, stages, SAM install) is not covered here.

---

## What `lambdaNames` is

A single string listing every **`FunctionName`** your service deploys, across **all** nested `template.yaml` files. Names must match CloudFormation exactly.

Each name is the resolved value of:

```yaml
FunctionName: !Sub '${StackModifier}-<logical-suffix>'
```

Example suffixes: `flk-logon-app-config-api`, `flk-logon-app-tx-consumer`.

---

## Naming pattern

```
<stack-modifier-as-deployed>-<lambda-suffix>
```

- **`StackModifier`** comes from stack parameters (often includes environment, e.g. `dev-logon-app`).
- **`<lambda-suffix>`** is the static part after `${StackModifier}-` in the template.

If `StackModifier` is `dev-logon-app` and `FunctionName` is `!Sub '${StackModifier}-flk-logon-app-config-api'`, the full name is:

`dev-logon-app-flk-logon-app-config-api`

Use the **same convention per environment** your pipeline deploys (e.g. `qa-logon-app-...`, `prod-logon-app-...`) when maintaining separate Jenkinsfiles or branches—or keep one list per env if your repo does that.

---

## Example (multi-line Groovy string)

```groovy
def lambdaNames = """
  dev-logon-app-flk-logon-app-config-api,
  dev-logon-app-flk-logon-app-tx-consumer,
  dev-logon-app-flk-logon-app-tx-listener,
  dev-logon-app-flk-logon-app-cache-core-data,
  dev-logon-app-flk-logon-app-cache-resource,
  dev-logon-app-flk-logon-app-cache-user
"""
```

Pass `lambdaNames` to whatever step your **organization’s** Jenkins pipeline uses for registration; this skill does not define that step.

---

## How to build the list

1. Search all `**/template.yaml` under `application/` (and siblings) for `AWS::Serverless::Function`.
2. For each function, read **`FunctionName`** (often `!Sub '${StackModifier}-...'`).
3. Mentally substitute your real `StackModifier` for the target environment—or read a concrete name from an already-deployed stack / AWS console if unsure.
4. Add **every** function; omitting one means it may not be registered for tooling that relies on this list.

---

## Checklist

- [ ] Every `AWS::Serverless::Function` in every sub-stack appears in `lambdaNames`
- [ ] Each string equals the deployed **`FunctionName`** (no typos, no missing environment prefix)
- [ ] New Lambdas: update SAM first, then append to `lambdaNames` in the same change when possible
