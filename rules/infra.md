---
paths:
  - "**/*.tf"
  - "**/*.tfvars"
  - "**/amplify.yml"
  - "**/cdk.json"
  - "**/template.yaml"
  - "**/template.yml"
---

# Infrastructure-as-code rules

- Never commit `.tfvars` with real values. Use `.tfvars.example`.
- Never hardcode account IDs, ARNs, or region strings. Use variables.
- Terraform: match the formatting from `terraform fmt` -- never manual indent.
- AWS Amplify / CDK / SAM: keep IaC and runtime config in the same PR. Don't split.
- For upstream Terraform contributions, use the `oss` skill and read the project's CONTRIBUTING first.
