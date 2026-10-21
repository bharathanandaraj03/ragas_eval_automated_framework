# Orbitly Security and Compliance

> Fictional company and product, created as demo data for RAG evaluation.

## Certifications

Orbitly holds SOC 2 Type II and ISO/IEC 27001 certifications. Audit reports are available to customers under NDA on request. Orbitly is GDPR compliant and offers a Data Processing Agreement (DPA) to all paid customers. Orbitly is **not** HIPAA compliant and must not be used to store protected health information.

## Data residency

Customer data is hosted on AWS. Customers choose a data region when creating a workspace:

- United States (us-east-1, Virginia) — default
- European Union (eu-central-1, Frankfurt)
- Australia (ap-southeast-2, Sydney)

The data region cannot be changed after the workspace is created. To move regions, customers must export data and import it into a new workspace.

## Encryption

- Data in transit is encrypted with TLS 1.2 or higher.
- Data at rest is encrypted with AES-256.
- Enterprise customers can bring their own encryption keys (BYOK) via AWS KMS.

## Authentication

- All plans support email/password login and Google sign-in.
- Two-factor authentication (2FA) using an authenticator app is available on all plans; workspace Owners on Business and Enterprise can enforce it for all members.
- SAML SSO (Okta, Azure AD/Entra ID, OneLogin) is available only on Enterprise.
- Passwords must be at least 12 characters long.
- Sessions expire after 30 days of inactivity on Starter and Business; Enterprise admins can configure session length from 1 hour to 30 days.

## Backups and data retention

Backups are taken every 6 hours and retained for 35 days. Deleted tasks and projects go to the Trash and can be restored for 30 days. After a workspace is cancelled, data is deleted within 90 days unless the customer requests earlier deletion.

## Vulnerability disclosure

Security issues can be reported to security@orbitly.example. Orbitly runs a private bug bounty programme and commits to acknowledging reports within 2 business days.
