# Security Policy

## Reporting Security Issues

If you discover a security issue, credential exposure, or sensitive information accidentally committed to the repository, please do not open a public issue.

Instead, contact the repository maintainer privately.

## Repository Security Standards

This repository uses the following practices:

- GitHub secret scanning
- Pull request review workflows
- .gitignore rules for credentials and local configuration
- Environment-variable-based credential management

## Never Commit

- API keys
- Tokens
- Passwords
- SSH keys
- QuantConnect credentials
- WRDS credentials
- Local machine paths containing personal information

## Student Guidance

Students contributing to this repository should:

- Use .env files locally
- Never hard-code secrets into notebooks or scripts
- Review notebook outputs before committing
- Remove sensitive metadata from exported files
