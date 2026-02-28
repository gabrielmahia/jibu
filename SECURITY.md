# Security Policy

## Reporting a Vulnerability

If you discover an error:

DO NOT open a public issue.

Email directly to:
contact@aikungfu.dev

## Scope

Security issues in this SDK include:
- Credential leakage (consumer key/secret, OAuth tokens)
- Incorrect signature or password generation that could lead to rejected payments
- Callback verification bypass vulnerabilities
- Dependency vulnerabilities (currently: zero runtime dependencies)

## Credential safety

`MpesaClient` stores credentials in memory only. They are never logged, written to disk, or sent to any endpoint other than the official Safaricom Daraja API (`sandbox.safaricom.co.ke` or `api.safaricom.co.ke`).

Never commit credentials to source control. Use environment variables or a secrets manager.
