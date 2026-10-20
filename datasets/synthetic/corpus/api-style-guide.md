# API Style Guide

Nimbus Dynamics public and internal API style guide, version 3. Owned by the Architecture Council.

## Resource Design

APIs expose resources as nouns, not verbs: `GET /orders/{id}`, not `GET /getOrder`. Collections support pagination with cursor tokens rather than offsets.

## Errors

Errors return structured bodies with a stable machine-readable `code`, a human-readable `message`, and a `retry_after` field when the error is transient. HTTP status codes follow standard semantics; 429 responses always include `retry_after`.

## Versioning

APIs version through URL prefixes (`/v1/`, `/v2/`). Breaking changes require a new version and a migration guide published 90 days before deprecation of the old version.

## Idempotency

All POST endpoints that create resources accept an idempotency key header. Retrying with the same key returns the original result instead of creating a duplicate.

## Security

Internal APIs authenticate with short-lived service tokens. No endpoint accepts credentials in query strings. Rate limits are documented per endpoint and enforced at the gateway.
