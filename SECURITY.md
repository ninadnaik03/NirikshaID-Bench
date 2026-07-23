# Security

## Supported scope

NirikshaID Bench is a research demonstration, not a production identity-verification or fraud-detection system. It must not be used to make decisions about real people or real identity documents.

## Reporting a vulnerability

Please report security issues privately through the contact options on [Ninad Naik's GitHub profile](https://github.com/ninadnaik03). Do not open a public issue containing credentials, personal data, exploit payloads, or real identity documents.

## Data-handling expectations

- Never upload real identity documents to the demo.
- Never commit `.env` files, API keys, model credentials, or deployment tokens.
- Use only synthetic generated samples in issues and pull requests.
- Treat visual prompt-injection examples as untrusted document content.
- Review CORS and upload-size settings before any deployment.
