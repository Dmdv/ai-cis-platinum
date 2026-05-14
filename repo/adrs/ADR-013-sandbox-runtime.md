# ADR-013 — Sandbox runtime for MCP code execution

**Contents**

- [Decision](#decision)
- [Rationale](#rationale)
- [Consequences](#consequences)
- [Alternatives considered](#alternatives-considered)
- [Revisit conditions](#revisit-conditions)


**Status:** Accepted.
**Date:** 2026-05-14.
**Context:** Pillar 3 Component 3.4.1 commits the platform to the MCP code-execution pattern: the Design agent (and any fan-out screen — e.g. the 5,124-inference-call fragment-assembly sweep) emits a single Python block that runs against the platform's MCP tool surface, returning only the ranked result to the model. **The sandbox runtime that hosts this code is a load-bearing component not previously specified in the service catalogue.** This ADR fixes that gap.

## Decision

Adopt **Pyodide (CPython-in-WASM)** as the Phase-1 sandbox runtime for MCP code-execution blocks, hosted as a service-internal microservice (`mcp-code-runner`) that the `agentic-orchestrator` calls via gRPC. **gVisor + CPython** is the Phase-2 / Phase-3 graduation when (a) Pyodide's package coverage limits production work, or (b) the sandbox runtime needs to call host-side native binaries (RDKit C++ bits, AiZynthFinder, ORCA).

| Phase | Runtime | Why |
| --- | --- | --- |
| Phase 1 | **Pyodide** (CPython 3.11 in WebAssembly, hosted inside a Node / Deno worker) | Memory-bounded, no host-FS access by default, no networking by default, predictable cold-start ≤ 2 s. ~95 % of the PyPI ecosystem available pre-built; numpy / pandas / pydantic / requests cover the Design-agent screen workload. |
| Phase 2-3 graduation | **gVisor + CPython 3.11** in a per-execution ephemeral container | Full Python ecosystem (RDKit C++, AiZynthFinder, ORCA); strong syscall-level isolation via gVisor; ~5-10 s cold-start. Reserved for code blocks that demonstrably need native binaries. |

The sandbox runtime is a **separate service from the agentic-orchestrator** (`mcp-code-runner` in `repo/services/`) so that compromised sandboxes cannot reach into orchestrator state. The runner exposes a single RPC: `execute_block(code: str, mcp_servers: list[MCPServerRef], time_budget_s: int) -> ExecutionResult`. All MCP tool calls from sandboxed code flow through the runner's outbound proxy, not directly to the MCP servers.

## Rationale

- **Pyodide is mature in 2026.** Anthropic's own MCP code-execution patterns (per the *Code execution with MCP* article) reference Pyodide-style sandboxes; the runtime is no longer experimental.
- **The Design agent's typical workload (5,124-call fragment screen, numpy / pandas / pydantic) fits inside Pyodide without modification.** No RDKit C++ bindings are required — the screen calls `inference-api` via HTTP, which Pyodide supports natively.
- **WASM sandbox boundary is hardware-enforced** in modern engines (V8, SpiderMonkey, JSC). The agent's code cannot escape the WASM heap into the runner process without an engine-level vulnerability.
- **Cold-start budget ≤ 2 s** keeps the Design agent's fan-out screen within the campaign's latency budget. gVisor's 5-10 s cold-start would dominate the Design-agent step time.
- **gVisor is the right Phase-2 graduation** when RDKit / AiZynthFinder / ORCA need to run inside the sandbox. gVisor's syscall interception provides a strong isolation boundary while permitting native binaries.

## Consequences

- A new service (`mcp-code-runner`) joins the catalogue. Phase-1 implementation is a thin Node / Deno wrapper around `@pyodide/pyodide`.
- The agentic-orchestrator's tool surface to `mcp-code-runner` is bounded to a single RPC; the runner does the MCP fan-out, not the orchestrator.
- The runner is the chokepoint for outbound network traffic from sandboxed code. All MCP server URLs and credentials live in the runner, not in the agent prompt.
- A second runner (gVisor) is built in Phase 2/3 only when Pyodide's coverage limits work.
- Per-execution time budgets are enforced at the runner level; runaway code blocks are killed without leaking resources back into the orchestrator.
- Observability per code-execution block: `code_exec_duration_ms`, `code_exec_mcp_calls`, `code_exec_token_input`, `code_exec_token_output`, all tagged with `campaign_id` + `agent_id` + `runner_kind` ("pyodide" / "gvisor").

## Alternatives considered

- **Deno Worker (TypeScript sandbox, no Python).** Compelling for tool-use sandboxes where agents emit TypeScript. Rejected for Phase 1 because the Design agent reasoning over chemistry libraries (numpy / pandas / pydantic) is much more natural in Python than TypeScript; the team's chemistry-aware code is Python-native.
- **Firecracker microVMs.** Stronger isolation than gVisor; chosen by some MCP-as-a-service providers. Rejected as overkill for an academic-lab system; the cold-start (200 ms) is acceptable but the operational complexity of running a per-execution microVM fleet is not worth it for the Phase-1 scale.
- **In-process Python (no sandbox).** Rejected — agent-emitted code with no isolation boundary is a category of risk we don't accept.
- **Sandbox as a third-party SaaS (e.g. E2B, Modal).** Rejected on data-sovereignty grounds — pre-publication compound structures cannot transit external sandboxes per ADR-007 and the Pillar 3 data-sovereignty argument.

## Revisit conditions

- Pyodide stops being maintained or its WASM build coverage degrades.
- The Design agent's typical workload starts requiring RDKit C++ bindings or other native dependencies — promote to the gVisor runner.
- A serious security advisory affects the chosen runtime.
- The MCP code-execution pattern is supplanted by a different agentic-execution paradigm (e.g. agent-internal direct tool calling becomes more efficient than code execution at the lab's scale).
