# Magitek – terms of reference

- **Status:** Draft v0.1; proposed requirements with unresolved qualification
  questions. This document makes no implementation or release claim.
- **Date:** 2026-11-19.
- **Audience:** Magitek maintainers, Rust agent-host implementers, Podbot and
  Corbusier integrators, and reviewers of protocol and resource guarantees.
- **Companion documents:** [Context and vocabulary](context.md),
  [technical design](magitek-design.md), and [GIST roadmap](roadmap.md).

## 1. Background and motivation

Agent hosts need a resource contract for their protocol connections. A host
must remain able to observe, cancel, and close work while an agent produces
output, requests permission, or stops reading. An asynchronous interface alone
does not establish that contract. Nor does one bounded queue establish a bound
on the resources that the entire connection retains.

The immediate demand comes from two related bodies of work. The planned Rust
replacement for the Lody command-line interface and daemon needs ACP agent
hosting that does not compete with heartbeat and synchronization progress.
Podbot already proxies agent protocol traffic across a sandbox boundary and
plans a typed hosted-session interface for embedders such as Corbusier. These
consumers need common protocol guarantees while retaining different process,
policy, and persistence responsibilities.[^1]

Existing Podbot source provides concrete motivation. It bounds several proxy
buffers and routes synthesized replies through a single stdin owner. Its
outbound frame assembler also switches to unrestricted forwarding after an
oversize unterminated frame. That behaviour preserves byte forwarding but
cannot satisfy a strict ACP enforcement contract. Sharing the resource and
failure contract creates an opportunity to resolve these choices once, with
evidence that both consumers can use.[^2]

The brief authorizes a library investigation. It establishes no external
demand, delivery date, or production result. The design and roadmap remain
proposals until review.

## 2. Domain

Magitek operates in agent-host infrastructure. The Agent Client Protocol (ACP)
defines communication between a client and an agent. In this project, the
embedding application occupies the client side even when it runs as a daemon
and launches the agent. An agent can send notifications and make requests back
to that client. The host must therefore continue servicing both directions
while a prompt remains outstanding.

The central terms are *connection*, *session*, *operation*, *admission*,
*budget*, *delivery*, and *outcome*.
[Context §2](context.md#2-domain-vocabulary) defines them. A transport
connection does not establish a session's durable identity. Transport delivery
does not establish execution. A locally expired deadline does not prove that an
agent stopped.

Compatibility determines which messages and capabilities a peer understands.
Operational correctness determines what happens when a consumer falls behind, a
callback stalls, or the connection closes with work outstanding. Magitek must
describe both duties without inventing guarantees that ACP or the host cannot
provide.

The brief establishes no sector-specific regulatory requirement. Hosts retain
their deployment obligations and choose which agent capabilities to authorize.

## 3. Market and prior-art context

The initial alternative is application-specific integration. The Rust ACP SDK
offers a protocol foundation; Podbot supplies a sandbox proxy; each host can
write the scheduling and lifecycle glue around them. Magitek must justify its
maintenance cost by making those operational contracts reusable.

| Alternative                       | What it contributes                                                      | Question Magitek must answer                                                                                          |
| --------------------------------- | ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| Official Rust ACP SDK             | Typed protocol definitions and connection machinery.                     | Can the selected version provide the required limits and progress rules directly or through a narrow upstream change? |
| Agentkit SDK                      | A candidate transport path with explicit admission and resource charges. | Can the complete high-level path retain those bounds while meeting the chosen protocol profile?                       |
| Mango ACP harness                 | A bounded peer beneath an application-oriented harness.                  | Can the reusable peer preserve the required event fidelity without importing harness policy?                          |
| Podbot's existing proxy           | Sandbox transport, capability masking, and bounded proxy buffers.        | Which lower-level framing and enforcement contracts can serve both a proxy and a full client?                         |
| Wireframe                         | Proposed bounded framing, reservation, and full-duplex primitives.       | Do the delivered primitives hold their bounds beneath the selected protocol engine?                                   |
| Separate integration in each host | Immediate control over application-specific behaviour.                   | Can one shared implementation remove duplicated protocol failure handling without widening its scope?                 |

*Table 1: Existing alternatives and the evidence needed to justify reuse.*

The SDK remains the preferred foundation to qualify. The brief does not choose
between upstream reuse, a small patch, or a different protocol engine. Magitek
plans to obtain budgeting and stream parsing from Wireframe beneath that
engine, as
[ADR 0001](adrs/adr-0001-reuse-wireframe-for-budgeting-and-stream-parsing.md)
records. The qualification decision must compare measured behaviour and
maintenance cost; wrapping an existing engine does not establish bounds inside
that engine. [Context §3](context.md#3-evidence-and-knowledge-status) records
the source baseline and the distinction between observation and proposal.

## 4. Users and stakeholders

The primary users are Rust engineers embedding agent connections. They already
own application state and supervision. They need precise behaviour under
failure, typed events that retain useful protocol information, and an interface
that does not require them to adopt another orchestration system.

| Role                              | Working context and need                                                                                                                  | Existing alternative                                               |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Rust Lody-replacement implementer | Runs a long-lived daemon with synchronization, liveness, and agent work; needs protocol work to respect the daemon's resource boundaries. | Add protocol integration and hardening inside the daemon.          |
| Podbot or Corbusier embedder      | Connects to sandboxed agents and governs their capabilities; needs the same client contract across supplied transports.                   | Combine Podbot byte streams with application-specific client code. |
| Maintainer and incident reviewer  | Diagnoses incomplete operations, overload, and peer incompatibility; needs evidence that distinguishes those conditions.                  | Infer state from logs and application-specific timeout handling.   |
| Agent implementer                 | Checks whether an agent interoperates with the declared client profile.                                                                   | Reproduce each host's integration separately.                      |

*Table 2: Initial users and their current alternatives.*

df12 Productions maintainers act as the project stakeholders. Consumer
maintainers review whether the proposed boundary serves their applications.
Upstream SDK maintainers determine whether changes belong upstream; this plan
does not assign them work or assume acceptance.

Interactive end users encounter Magitek through a host. Agent authors, workflow
operators, and sandbox administrators have different primary jobs; protocol
SDKs, orchestration applications, and Podbot serve them directly.

## 5. Jobs to be done

When a daemon hosts agents alongside synchronization and liveness work, its
implementer wants protocol activity to remain within declared limits, so one
busy or stalled agent cannot silently consume the daemon's capacity or obscure
the status of accepted work.

When an orchestrator connects to an agent inside a sandbox, its implementer
wants a consistent client contract across the available transports, so changing
the execution environment does not require reimplementing request handling,
event ordering, and interruption semantics.

When a connection fails during an operation, its maintainer wants to identify
what the host admitted, what the transport may have delivered, and what the
agent reported, so recovery can preserve uncertainty instead of repeating an
action that may already have taken effect.

## 6. Scope

### 6.1 Goals

- **G1 – Account for retained resources.** Every resource that Magitek retains
  on behalf of a connection has a declared limit, owner, and release condition.
  Reaching a limit produces a documented result that preserves the contract.
- **G2 – Preserve progress or explain its loss.** Under the documented host
  execution conditions, slow consumers and ordinary callback work do not
  silently prevent protocol control and completion processing. A condition that
  prevents further progress ends in an explicit bounded failure path.
- **G3 – Preserve protocol information.** Hosts receive full-fidelity typed
  events for the supported profile, including relevant extension metadata and
  ordering relationships. The library reports unsupported input or delivery
  failure explicitly instead of silently summarizing or dropping it.
- **G4 – Expose uncertainty.** Callers can distinguish local admission,
  transport progress, peer response, cancellation intent, and interrupted or
  unknown outcomes. Reconnection never silently repeats uncertain actions.
- **G5 – Serve distinct hosts.** The Rust Lody replacement and a Podbot-backed
  embedding can use the same client contract while retaining their own
  authority, lifecycle, and persistence decisions.
- **G6 – Make claims reviewable.** The supported protocol profile, resource
  accounting, failure behaviour, and operational limits have reproducible
  qualification evidence and diagnostics that identify the relevant stage.

### 6.2 Non-goals

- **NG1 – Workflow orchestration.** Scheduling work, prioritizing repositories,
  assigning agents, and moving Ishiban cards remain application concerns.
  Magitek reports protocol evidence for applications to interpret.
- **NG2 – Execution infrastructure.** Process creation, sandbox provisioning,
  container or Pod lifecycle, machine registration, and fleet ownership remain
  host responsibilities. Magitek consumes their transport and status contracts.
- **NG3 – Durable application state.** Transcript storage, command journals,
  synchronization, conflict-free replicated data types, and recovery across
  daemon restarts belong to the host. Event delivery alone establishes no
  persistence guarantee.
- **NG4 – Permission policy.** Magitek transports and bounds reverse requests;
  the host authorizes filesystem access, terminal operations, and tool use. The
  library does not acquire authority merely because a peer requests it.
- **NG5 – Arbitrary replay and universal compatibility.** Magitek does not
  guarantee exactly-once tool execution, transparent recovery of arbitrary
  agent operations, or support for every vendor extension. Qualification
  defines the supported profile.
- **NG6 – Whole-machine resource guarantees.** Accounted library resources do
  not establish a hard resident-memory ceiling or an absolute CPU-latency
  guarantee for the process. Allocators, host code, peers, the runtime, and the
  operating system retain separate costs and scheduling obligations.

## 7. Success criteria

The following criteria define required evidence, not achieved results. Numeric
latency and workload thresholds remain open until representative measurements
can justify them. Tests must record their host service assumptions.

| ID  | Outcome and falsifiable evidence                                                                                                                                                                                                      | Goals  |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| SC1 | Instrumented saturation tests keep every accounted resource within its configured limit; ownership transitions explain retained resources until release. Independent memory measurements identify costs outside that accounting.      | G1, G6 |
| SC2 | Combined slow-consumer, reverse-request, blocked-write, and diagnostic-load scenarios either preserve eligible protocol progress or produce the documented terminal failure within the configured observation and shutdown deadlines. | G1, G2 |
| SC3 | A compatibility corpus preserves supported content, extension metadata, and required protocol order through typed delivery; public completion does not overtake preceding required events.                                            | G3, G6 |
| SC4 | Fault injection around admission, partial writing, peer response, cancellation, and disconnect returns the specified outcome without automatic replay of uncertain work.                                                              | G4     |
| SC5 | The Rust Lody replacement and a real Podbot-backed integration pass the shared client contract without transferring lifecycle, permission policy, or persistence into Magitek.                                                        | G5     |
| SC6 | An operator can distinguish overload, peer silence, host callback delay, protocol incompatibility, and transport interruption from bounded status and diagnostics; diagnostic sinks cannot silently stall protocol work.              | G2, G6 |

*Table 3: Acceptance evidence for the initial product boundary.*

For daemon adoption, SC5 covers local command and history persistence. An
independent reader must verify the persisted result. Cloud catalogue and
replication convergence remain separate daemon qualification gates.

SC5 provides the adoption signal; SC1, SC2, SC4, and SC6 provide operational
evidence. Shared qualification and removal of duplicated failure handling
justify the investment. The brief establishes no revenue or market targets.

## 8. Constraints and assumptions

### 8.1 Hard constraints

The requested implementation target is native asynchronous Rust. Integration
must keep substantial parsing, callbacks, persistence, and diagnostics away
from paths whose progress the host relies on. The design must state the
execution service that the host supplies; merely moving work into a task does
not establish isolation.

Podbot retains its execution and proxy roles. Its hosted-session interface and
Kubernetes work remain proposals at the recorded source baseline.[^3] Magitek
must not require Kubernetes before demonstrating the shared client boundary.
The read-only Ishiban observation spike in the Lody plan must also remain
independent of ACP library delivery.

Capability enforcement must not weaken when a resource limit or parsing error
occurs. Unsupported profiles fail explicitly. Diagnostics must exclude secret
values by default and must avoid retaining arbitrary prompts or transcripts
merely to explain connection health.

### 8.2 Assumptions

| ID  | Assumption pending verification                                                              | Consequence if false                                                                                             |
| --- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| A1  | The official SDK or a narrow change can support the operational contract.                    | Reassess the protocol-engine boundary and maintenance cost before committing to an implementation basis.         |
| A2  | Both initial consumers can provide independently driven transport and lifecycle information. | Define the missing consumer contract before claiming integration compatibility.                                  |
| A3  | Representative agents accept explicit frame and concurrency limits.                          | Narrow the supported profile or revise limits using evidence; retain explicit rejection rather than silent loss. |
| A4  | Consumers can state when they release or persist a delivered event.                          | Keep resource ownership explicit and withhold any downstream durability claim.                                   |
| A5  | Wireframe delivers its proposed framing and reservation contracts for a standalone consumer. | Keep the dependent tasks blocked and select another source through a superseding decision record.                |

*Table 4: Load-bearing assumptions and their failure consequences.*

### 8.3 Dependencies

ACP specifications and the selected SDK establish compatibility inputs. Agent
implementations supply interoperability evidence. Wireframe supplies the
planned framing and reservation primitives; the roadmap names the Wireframe
task that gates each dependent Magitek task. Podbot's transport and control
interface supplies the sandboxed-consumer boundary. The Rust Lody-replacement
project supplies the second consumer and its persistence contract. None of
these dependencies implies automatic upstream acceptance, an available
hosted-session API, or a release date.

## 9. Open questions

Owners below name implementation roles without assigning external maintainers
work. Gates map to phases in [roadmap.md](roadmap.md).

| ID  | Question and reason                                                                                                     | Resolution evidence                                                                           | Owner role and gate                                           |
| --- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| OQ1 | Which SDK integration satisfies end-to-end limits and ordering? It determines the implementation basis.                 | Source audit, boundedness experiments, and a recorded upstream-versus-local decision.         | Protocol maintainer; phase 1.                                 |
| OQ2 | Which protocol version, capabilities, and agents define the first profile? It bounds compatibility claims.              | A versioned conformance corpus and real-agent results.                                        | Protocol maintainer with consumer owners; phases 1, 2, and 4. |
| OQ3 | Which budgets and latency thresholds fit actual workloads? Arbitrary defaults can reject useful work or hide backlog.   | Representative traces, stress measurements, and declared host execution conditions.           | Performance reviewer; phases 2 and 4.                         |
| OQ4 | How should hosts treat large resources and unknown extensions? Lossless delivery must respect finite limits.            | Explicit limits and rejection or opt-in rules, tested with multimodal and extension fixtures. | Protocol maintainer with consumer owners; phases 2 and 3.     |
| OQ5 | Which transport and lifecycle facts can consumers establish after disconnect? They constrain outcome classification.    | Fault tests covering process status, partial writes, and unverified termination.              | Podbot and daemon integration owners; phases 3 and 4.         |
| OQ6 | Which runtime, compiler, and platform profiles form the release contract? Unsupported combinations must remain visible. | Maintainer decision and reproducible build and interoperability checks.                       | Magitek maintainer; phases 1 and 4.                           |

*Table 5: Decisions that remain open and the evidence that closes them.*

## 10. Handoff and change control

OQ1 and OQ2 gate the implementation foundation. Later evidence can resolve the
remaining questions within the product boundary. No open question permits a
silent fallback that violates G1–G6.

[ADR 0001](adrs/adr-0001-reuse-wireframe-for-budgeting-and-stream-parsing.md)
records the planned reuse of Wireframe. Candidate architectural decision
records should cover the SDK integration basis, the event-ownership boundary,
and the supported transport and protocol profiles.
[magitek-design.md](magitek-design.md) records proposed mechanisms;
[roadmap.md](roadmap.md) sequences the evidence and implementation work.
Changes to users, goals, or non-goals update this document first. Changes to
terminology update [context.md](context.md) and dependent documents together.

## References

Sources below were inspected on 2026-11-14. The context document records the
broader evidence ledger and the status of each source.

[^1]: Project brief and approved scope recorded in
    [context.md §1](context.md#1-project-brief), plus Podbot's proposed
    [hosted-session interface][podbot-session].

[^2]: Podbot's [stdin owner and queue][podbot-runtime] and
    [outbound frame assembler][podbot-frames], pinned to commit
    `c2c3b232730cea3ac8a88adde06d43c2e93cb309`.

[^3]: Podbot [ADR 002][podbot-session], status Proposed, and
    [Kubernetes RFC][podbot-kubernetes] on open pull request 285, pinned to
    `fa0be50ae147acd53e1f374ba2971b1c1f67f0b9`.

[podbot-session]: https://github.com/leynos/podbot/blob/c2c3b232730cea3ac8a88adde06d43c2e93cb309/docs/adrs/adr-0002-define-the-hosted-session-api-and-control-channel.md
[podbot-runtime]: https://github.com/leynos/podbot/blob/c2c3b232730cea3ac8a88adde06d43c2e93cb309/src/engine/connection/exec/acp_runtime.rs
[podbot-frames]: https://github.com/leynos/podbot/blob/c2c3b232730cea3ac8a88adde06d43c2e93cb309/src/engine/connection/exec/acp_frame.rs
[podbot-kubernetes]: https://github.com/leynos/podbot/blob/fa0be50ae147acd53e1f374ba2971b1c1f67f0b9/docs/rfcs/0001-kubernetes-execution-backend.md
