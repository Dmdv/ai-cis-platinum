# ADR-007 — Model Context Protocol (MCP) as the tool surface contract

**Contents**

- [Decision](#decision)
- [Rationale](#rationale)
- [Consequences](#consequences)
- [Alternatives considered](#alternatives-considered)
- [Revisit conditions](#revisit-conditions)


**Status:** Accepted.
**Date:** 2026-05-14.
**Context:** Pillar 3 (the agentic orchestrator) introduces a tool-call surface that exposes the lab's chemistry capabilities (chemoinformatic-core sanitization, inference-api prediction, retrosynthesis, ELN, knowledge-graph query) to LLM agents. The choice of wire protocol determines portability, interoperability with external AI clients, and resilience to agent-framework churn.

## Decision

The lab adopts Anthropic's **Model Context Protocol (MCP)** as the primary tool-surface contract. Every service in Pillar 4 ships an `mcp-server` mode alongside its REST API. The internal Python `Tool` protocol (see `docs/05_pillar3_agentic_dmta.md` Component 3.4) remains as the type-safe in-process contract; MCP is the external wire format.

## Rationale

- **2025-2026 standardisation.** MCP was released by Anthropic in Dec 2024; OpenAI adopted it in March 2025; Google in mid-2025; Cursor and most agent IDEs by Q4 2025. It was donated to the Linux Foundation's Agentic AI Foundation in December 2025. By mid-2026 it is the de-facto agent-tool wire format. The official MCP documentation (`modelcontextprotocol.io`) captures the analogy directly: *"Think of MCP like a USB-C port for AI applications. Just as USB-C provides a standardized way to connect electronic devices, MCP provides a standardized way to connect AI applications to external systems."* For a 2026 grant reviewer, this is the right level of abstraction: a research-application proposal that anchors its tool surface on a "USB-C-like" open standard is forward-compatible by construction.
- **LangGraph independence.** Tools defined as MCP servers are not coupled to LangGraph (the chosen orchestrator framework, ADR-004). If LangGraph fails as a project or a better orchestration framework emerges, the tools survive intact.
- **Multi-client reuse.** A chemoinformatic-core MCP server is callable not just by the lab's orchestrator but also by Claude Desktop, OpenAI tool-use clients, Cursor, and any future LLM-driven analysis tool a lab member adopts. This is high-leverage for a small team.
- **Code-execution pattern (Anthropic, Dec 2025).** MCP enables the "agent writes code that calls MCP tools" pattern, vastly more efficient than tool-call-per-message for large fragment screens (427 scaffolds in the de novo round).

## Consequences

- Each service author writes both the REST handler and the MCP handler. The duplication is minor in Python (FastMCP or `mcp` SDK wraps the same function).
- MCP discovery / catalogue management becomes a new operational concern; addressed by an MCP registry pattern (`mcp://chemoinformatic.babaklab/sanitize`).
- Authentication / authorization for MCP servers must match the lab's existing API-key + OAuth posture.

## Alternatives considered

- **Custom OpenAPI tool format.** Considered; rejected because it would lock external AI clients out unless they adapt — which they won't.
- **OpenAI function-calling format.** Workable but vendor-tied. MCP supersedes this in practice.
- **No external protocol (Python-only).** The original design. Rejected on portability grounds — chemists' personal Claude Desktop clients should be able to talk to the lab's tools.

## Revisit conditions

- MCP loses momentum to a different standard.
- A wire-incompatible MCP v2 emerges and the team chooses to track or pin.
