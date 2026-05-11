# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.x     | Yes       |

## Reporting a vulnerability

Do **not** open a public GitHub issue for security vulnerabilities.

Email **taifooon@proton.me** with:
- A description of the vulnerability and its potential impact
- Steps to reproduce or a minimal proof-of-concept
- Your preferred contact for follow-up

We will acknowledge receipt within 48 hours and aim to ship a fix within 14 days for confirmed vulnerabilities. You will be credited in the release notes unless you prefer otherwise.

## Scope

This policy covers `taifoon-mamba` — the TSUL-licensed Pro dispatcher tier. For vulnerabilities in the open-core task bus (`open-mamba`) or on-chain contracts, use the same contact.

## Notes

- `taifoon-mamba` is source-available under TSUL v1.0. Commercial deployments routing value through the adapter fleet must preserve the `BuildersRegistry` donut routing — tampering with this is both a license violation and a security concern we take seriously.
