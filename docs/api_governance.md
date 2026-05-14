# API governance

**Contents**

- [Scope](#scope)
- [Versioning policy (semver)](#versioning-policy-semver)
- [Deprecation policy](#deprecation-policy)
- [Supported runtimes](#supported-runtimes)
- [Release cadence](#release-cadence)
- [Security-disclosure policy](#security-disclosure-policy)
- [Documentation source-of-truth](#documentation-source-of-truth)


This document defines the governance rules for every endpoint, SDK, and Skill the platform publishes externally. It is a load-bearing prerequisite for **B3.6 — Public API SDKs (Python, JS)** and **B3.4 — Skills marketplace public release** in Phase 3 of `docs/12_dual_track_milestones.md`. Without this contract, external consumers (other labs, MCP clients, third-party tools) face unbounded backwards-compatibility risk.

## Scope

The following surfaces are *public* and governed by this document:

- Endpoints under `https://<host>/api/v{N}/*` of any service (`inference-api`, `chemoinformatic-core`, `agentic-orchestrator`, `retrieval-service`).
- Officially-supported SDKs: **Python** (`pip install ai-cis-platinum`) and **JavaScript** (`npm install @ai-cis-platinum/sdk`).
- MCP server contracts published to the Skills Hub (per ADR-007 + ADR-011).
- The wire-level Pydantic / Protobuf schemas in `repo/services/chemoinformatic-core/src/schemas.py` (see `SCHEMA_VERSION`).

Endpoints under `https://<host>/api/internal/*`, unversioned routes, and any route returning a `Deprecation:` HTTP header are *internal* and not governed by this document.

## Versioning policy (semver)

The platform follows **semantic versioning** at three layers:

| Layer | Rule | Bumps |
| --- | --- | --- |
| **API path** | `/api/v{MAJOR}/...` | Bumped on any breaking change to request / response shape, status codes, or auth scheme. Multiple major versions may coexist during a deprecation window. |
| **SDK package** | `MAJOR.MINOR.PATCH` per pkg | Major = breaking; Minor = additive (new optional fields, new endpoints, new SDK methods); Patch = bug fixes and doc updates. |
| **Schema** | Integer `SCHEMA_VERSION` per contract module | Bumped on any breaking wire-format change. Additive fields keep the version. |

**Breaking changes** = renaming a field, changing a field's type, making a previously-optional field required, removing an endpoint, tightening an auth scope, returning a different status code for the same condition.

**Additive changes** = adding an optional field, adding a new endpoint, adding a new SDK method, loosening (not tightening) input validation.

## Deprecation policy

A public endpoint, SDK method, or schema field is marked deprecated by setting the `Deprecation:` HTTP response header (RFC 9745) and adding a `@deprecated` decorator / TypeScript tag in the SDK.

**Deprecation window:**

- **At least 2 minor SDK releases** AND
- **At least 6 months wall-clock** (whichever is longer)

After the deprecation window, the endpoint / method / field may be removed in the next major version. The removal is announced in the release notes one minor release in advance.

**Skills Hub items** declare `compatibility: api-v1+` in their frontmatter; a Skill that depends on a deprecated endpoint is auto-flagged and reviewed for migration.

## Supported runtimes

| Surface | Minimum supported | Notes |
| --- | --- | --- |
| Python SDK | **3.11+** | Drops Python 3.10 in line with NEP-29 / Anthropic SDK conventions. |
| JavaScript SDK | **Node 20 LTS+** (and modern browsers via ES modules) | Drops Node 18 LTS at its EOL. |
| Containers / orchestration | Kubernetes ≥ 1.28 | Tracks ≥ 2 currently-supported minor releases. |
| MCP servers | MCP spec version published in `modelcontextprotocol.io` at SDK release time, plus the prior version | Two-version compat band. |

Supported-runtime drops are announced one minor SDK release in advance.

## Release cadence

- **SDKs:** monthly minor releases (additive); patch releases ad-hoc for security or critical bugs.
- **API path major versions:** annual at most; only when deprecation windows of prior version have closed.
- **Schemas:** bumped only when wire-format changes require it; never as part of a routine release.

Every release ships:

- A `CHANGELOG.md` entry tagged `[Added] / [Changed] / [Deprecated] / [Removed] / [Fixed] / [Security]` per Keep-a-Changelog convention.
- Migration notes for any deprecation introduced in this release.

## Security-disclosure policy

- **Reporting channel:** `security@<host>` (email). PGP key published at `https://<host>/.well-known/security.txt`.
- **Acknowledgement:** within 5 business days.
- **Triage and fix target:** 30 days for confirmed vulnerabilities of CVSS ≥ 7.0; 90 days for lower-severity.
- **Coordinated disclosure:** 90-day disclosure clock from the date of confirmed reproduction. The platform follows Project-Zero-style 90-day discipline; extensions granted only when actively coordinating with affected downstream consumers.
- **CVE assignment:** the platform is a CVE Numbering Authority of last resort; reporters are invited to coordinate with MITRE.
- **Bounty:** none in the current academic-budget regime; documented credit in release notes.

## Documentation source-of-truth

- **OpenAPI 3.1** is the single source of truth for every public REST endpoint. SDKs are generated from the OpenAPI spec; hand-written client code is not the source of authority.
- **MCP server tool schemas** are published as JSON schemas under `https://<host>/.well-known/mcp/<server>.json`.
- **Schema versions** are exposed as a `Schema-Version: 1` HTTP header on every response so clients can record reproducibility metadata.
- **SDK reference docs** are generated from docstrings; out-of-band documentation is forbidden.

If the OpenAPI spec, the SDK, and the implementation disagree, the OpenAPI spec wins and the others are fixed.
