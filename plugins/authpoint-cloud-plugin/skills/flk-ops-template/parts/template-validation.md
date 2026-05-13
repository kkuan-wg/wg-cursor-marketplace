# Template validation, parameters, and review

Use when **authoring or reviewing** SAM/CloudFormation: catch dead parameters, broken references, and API definitions split across YAML + Swagger.

---

## Tracing and X-Ray

- `Globals.Function.Tracing` must be **`Disabled`**; `AWS::Serverless::Api.TracingEnabled` must be **`False`** (see [api-gateway.md](api-gateway.md)).
- Do **not** add standalone **`AWS::XRay::*`** resources unless there is an explicit organizational exception.

---

## Parameters must be used

Every `Parameters` entry must be referenced somewhere meaningful:

- In the **same** `template.yaml` (`!Ref`, `!Sub`, `Fn::Sub`, conditions, nested `Parameters:` passthrough).
- In an **included OpenAPI/Swagger** file when `DefinitionBody` uses `Fn::Transform` / `AWS::Include` — parameters often appear only under `Fn::Sub` in `swagger.yaml`, not in the parent template.

**Before removing a “unused” parameter:** search the co-located Swagger/OpenAPI path referenced by `AWS::Include`.

**Before merge:** remove parameters that are truly dead (no references in template, nested params, or included spec).

---

## References must resolve

- Every `!Ref Name` must name a **Parameter** or **Resource** in scope (same template, or inherited in the way CloudFormation resolves for that file).
- Every `!GetAtt LogicalId.Attribute` must use a **real** logical id and a **valid** attribute for that resource type.
- Nested stacks: verify outputs exist on the child template when using `!GetAtt ParentStack.Outputs.Key`.

---

## API Gateway + Swagger

When the API uses `DefinitionBody` → `AWS::Include` → `swagger.yaml`:

- [ ] Lambda ARNs, URLs, and stage variables in the spec match resources in the SAM template.
- [ ] Parameters referenced only in Swagger are **not** flagged as unused without opening the spec file.

See [api-gateway.md](api-gateway.md) for the include pattern.

---

## Validation commands

```bash
sam validate --template path/to/template.yaml
cfn-lint path/to/template.yaml
```

Run against **root** and any **heavily edited** sub-stack templates. Fix linter errors before merge when they indicate real issues.

---

## Review report shape

When producing a written review, group findings by severity (use this structure when the output is a review document; skip for pure authoring tasks):

1. **Critical** — blocks deploy or violates mandatory Folklore/security rules (encryption, tracing, missing LogGroup, broken refs).
2. **Important** — fix before production (wrong VisibilityTimeout pattern, missing DLQ, overly broad IAM).
3. **Suggestion** — hygiene (naming, comments, minor cost/ops improvements).

End with a short **checklist** tied to [SKILL.md](../SKILL.md) **General Checklist** and the part-specific checklists (globals, lambda, sqs, api-gateway, nested-stacks, jenkinsfile).
