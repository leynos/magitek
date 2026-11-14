# Magitek – context and vocabulary

- **Status:** Draft v0.1; vocabulary and evidence baseline for a proposed
  library. No runtime implementation or qualification result exists here.
- **Date:** 2026-11-14.
- **Audience:** Maintainers and embedding-application implementers.
- **Companion documents:** [Terms of reference](terms-of-reference.md),
  [technical design](magitek-design.md), and [GIST roadmap](roadmap.md).

## 1. Project brief

Magitek addresses shared requirements of a native Rust Lody replacement and
Podbot-backed hosts such as Corbusier. The brief calls for a bounded
asynchronous Agent Client Protocol (ACP) client, with substantial work kept
away from event loops. The proposed boundary preserves protocol information
and exposes uncertainty.

The Lody replacement needs agent hosting alongside synchronization and
liveness. Podbot can reuse framing and accounting as a proxy; an embedding
application can use the full client above its transport. Podbot's proposed
hosted-session interface separates protocol streams from lifecycle and
hook-control events.[^1]

The commission of 2026-11-14 supplies the users, Rust target, and library
scope. It supplies no benchmark, released interface, or external adoption.
[Terms of reference §§6–9](terms-of-reference.md#6-scope) record the scope,
acceptance evidence, assumptions, and open questions.

## 2. Domain vocabulary

These definitions govern the companion documents. API names in the technical
design remain proposals; the vocabulary does not promise particular symbols.

### 2.1 Actors and identities

| Term | Meaning |
| --- | --- |
| Host application | The embedding program. It owns execution placement, permission policy, persistence, and execution service for library tasks. |
| ACP client | The protocol role that initializes a connection, creates or loads sessions, submits prompts, and services agent requests. A daemon can occupy this role. |
| Agent | The ACP peer accepting prompts and emitting updates or reverse requests, distinct from its model provider and container. |
| Proxy | An intermediary that forwards protocol bytes and may enforce declared policy. Reusing a codec does not make it a full ACP client. |
| Transport | The supplied input/output channels and their declared closure semantics. Lifecycle status can use a separate channel. |
| Connection generation | A connection instance and its correlation state. Replacement generations reject stale callback authority. |
| ACP session | A conversation identity established through ACP. It is not inherently a process, workflow task, repository, or durable application record. |
| Session generation | The local lifetime of a session route within a connection. Replacing that route fences its callbacks; the generation does not replace the opaque peer session ID. |
| Operation | One locally tracked request and its outcome. Its local identity does not establish peer deduplication or permit replay. |
| Turn | A prompt-oriented unit of agent work. Stable ACP session updates do not universally identify the originating turn. |

*Table 1: Actors and identities that must remain distinct.*

### 2.2 Resources and ownership

| Term | Meaning |
| --- | --- |
| Admission | The decision to accept work after reserving the resources required by its declared contract. Admission establishes no transport or execution result. |
| Budget | A configured limit on an accounted resource, such as retained bytes, queued items, active requests, or admitted work. A count limit alone does not bound payload size. |
| Payload byte charge | Accounting for retained wire-buffer capacity and decoded string, byte-array, and extension-payload capacity. It differs from encoded frame length and excludes allocator metadata. |
| Decoded node charge | Accounting for retained structural JSON elements, separately from payload bytes. Node count does not claim to measure their exact memory consumption. |
| Resource owner | The component or lease retaining a charge until release or explicit ownership transfer. |
| Event lease | A delivered event and its resource charge. Dequeueing alone does not release retained payloads. |
| Backpressure | Restricting further admission or reading because downstream capacity is unavailable. Backpressure can prevent progress on an ordered stream and therefore needs a failure policy. |
| Control reserve | Capacity retained for eligible responses and control work. It cannot bypass bytes already ordered ahead of a message or interrupt a partly written frame. |
| Deadline | A configured limit on waiting or progress observation under documented execution conditions. Expiry records a local fact, not proof of remote termination. |
| Accounted bound | A limit on resources within Magitek's stated ownership model. It is not a hard bound on process resident memory or total CPU service. |

*Table 2: Capacity terms and the limits of their guarantees.*

### 2.3 Information, progress, and outcomes

| Term | Meaning |
| --- | --- |
| Full-fidelity event | A typed event preserving supported content and extension metadata. Unsupported or oversized content produces an explicit result. |
| Session event sequence | Local event order, distinct from agent turn identity. Persistence across restart requires host storage. |
| Completion watermark | The required preceding event sequence associated with a peer result. It identifies the prefix that must reach the host before public completion. |
| Delivery watermark | The highest contiguous event sequence actually yielded as an event lease to the host. Enqueueing alone does not advance it; delivery establishes no durability or peer convergence. |
| Reverse request | An agent-to-client request, such as a permission, filesystem, or terminal request. The host supplies the authority and handler. |
| Cancellation intent | A local request to stop work, distinct from sending an ACP cancellation notification or receiving a terminal prompt result. |
| Interrupted outcome | The library lost the evidence needed to complete its normal protocol contract. The host may still have a running process. |
| Unknown outcome | Evidence cannot establish execution or completion. The host must reconcile or obtain a decision before replay. |
| Durability | Recovery of committed information after the relevant process or storage failure. The host defines this boundary; delivering an event does not establish it. |
| Fail closed | End or reject an enforced operation when the library cannot uphold its contract. Resource exhaustion must not silently disable capability enforcement. |

*Table 3: Observable facts and conclusions that do not follow from them.*

Public `PeerResult` completion requires the delivery watermark to reach the
completion watermark. Status can expose earlier peer terminal evidence with
`delivery_pending = true`; that evidence is not delivered completion. Neither
watermark proves durable storage or process exit.

One active prompt per session simplifies scheduling but cannot attribute every
session update to that prompt. A late or unsolicited update retains its session
identity unless the protocol supplies stronger evidence. The design must not
invent a turn identifier by attaching the currently active operation to every
event. ACP's [session-update schema][acp-schema] and
[prompt-turn description][acp-turn] supply the compatibility context.

## 3. Evidence and knowledge status

The documentation uses three knowledge classes:

- **Known:** an explicit requirement from the brief or an observation supported
  by an identified source. A known requirement describes desired behaviour; it
  does not establish implementation.
- **Assumed:** a load-bearing inference awaiting evidence. The terms of
  reference records the consequence if it fails.
- **Open:** a decision or fact not yet established. A named qualification gate
  must close it before dependent claims become valid.

Proposals describe intended mechanisms; correctness remains open until
qualification. Source inspection establishes code structure, not performance
or complete interoperability.

| Evidence | Status and significance |
| --- | --- |
| Project commission, 2026-11-14 | Known requirements: shared native Rust client, bounded work, explicit outcomes, and separate host responsibilities. |
| Official Rust ACP SDK at `05fd3893cca2f1be2eb3a262b0f7da2c52abaa58` | Known source baseline: SDK 5.3.0 and schema 1.18.0. Reuse remains the preferred qualification candidate, not an established implementation choice. |
| Podbot at `c2c3b232730cea3ac8a88adde06d43c2e93cb309` | Known implementation: protocol proxy, several explicit buffers, initialization masking, runtime policy, and a bounded stdin-command queue. |
| Podbot ADR 002 at the same commit | Known proposal: `HostedSession` separates protocol I/O from typed control events. Its status is Proposed; availability remains a downstream gate. |
| Podbot Kubernetes RFC at `fa0be50ae147acd53e1f374ba2971b1c1f67f0b9` | Known proposal in pull request 285: backend-neutral transport, initially unsupported reconnection, and later fenced supervision. It does not establish Kubernetes support. |
| Lody at `d3179e1f7538b61d0a6acc6be0a324281be4e3c0` | Known baseline for the preceding daemon investigation. Its deployment on any particular machine remains unverified. |
| Agentkit fork at `08355e7086a715be0a26b151d92f7c0812adda5d` | Known comparison candidate: SDK 3.6.0 with forked schema 1.14.0. A bounded transport surface alone does not qualify every high-level path. |
| Mango at `7b6bd40917f3d7275cbf2145f2970290e67bb3a0` | Known comparison candidate: the inspected branch identifies 0.8.0; inspected published documentation concerns 0.7.1. Keep those baselines separate. |

*Table 4: Evidence ledger; all external observations are source inspections.*

The [source list](#5-sources) provides immutable repository links. Official ACP
web pages are rolling documentation accessed on 2026-11-14. Their publication
state must not be represented as an invented source commit or equated with a
crate schema version.

## 4. Boundaries and unresolved tensions

Magitek owns its protocol contract and accounted resources. Hosts own process
placement, permission decisions, credentials, durable state, and recovery
policy. Podbot owns sandbox realization and proxy policy. Corbusier owns its
workflow decisions. The Lody replacement owns synchronization and presence;
Magitek's completion watermark cannot stand in for a durable transcript or a
peer's observation of synchronized history.

Three tensions require explicit qualification. Finite memory and lossless
delivery require a defined overload outcome. An ordered byte stream can block
control traffic behind data, even when internal queues reserve control
capacity. An external callback can consume resources beyond the library's
accounting unless the host supplies the agreed execution boundary.

The technical design resolves these tensions as proposed contracts. The
roadmap tests them before widening adoption. The first delivery gate requires
one local ACP client; real Podbot and daemon integration follow. Kubernetes,
distributed reconnection, and broader protocol profiles remain conditional.
Ishiban's read-only observation milestone does not depend on Magitek.

## 5. Sources

The following sources were inspected on 2026-11-14:

- [Official Rust ACP SDK source baseline][sdk].
- [ACP session-update schema][acp-schema] and
  [prompt-turn semantics][acp-turn], rolling official documentation.
- [Podbot source baseline][podbot],
  [stdin ownership and response queue][podbot-runtime], and
  [outbound frame assembler][podbot-frames].
- [Podbot proposed hosted-session interface][podbot-session] and
  [proposed Kubernetes backend][podbot-kubernetes].
- [Lody source baseline][lody].
- [Agentkit comparison baseline][agentkit].
- [Mango ACP harness design][mango].

[^1]: Podbot [ADR 002][podbot-session], status Proposed at the pinned commit.

[sdk]: https://github.com/agentclientprotocol/rust-sdk/tree/05fd3893cca2f1be2eb3a262b0f7da2c52abaa58
[acp-schema]: https://agentclientprotocol.com/protocol/v1/schema#sessionupdate
[acp-turn]: https://agentclientprotocol.com/protocol/v1/prompt-turn
[podbot]: https://github.com/leynos/podbot/tree/c2c3b232730cea3ac8a88adde06d43c2e93cb309
[podbot-runtime]: https://github.com/leynos/podbot/blob/c2c3b232730cea3ac8a88adde06d43c2e93cb309/src/engine/connection/exec/acp_runtime.rs
[podbot-frames]: https://github.com/leynos/podbot/blob/c2c3b232730cea3ac8a88adde06d43c2e93cb309/src/engine/connection/exec/acp_frame.rs
[podbot-session]: https://github.com/leynos/podbot/blob/c2c3b232730cea3ac8a88adde06d43c2e93cb309/docs/adrs/adr-0002-define-the-hosted-session-api-and-control-channel.md
[podbot-kubernetes]: https://github.com/leynos/podbot/blob/fa0be50ae147acd53e1f374ba2971b1c1f67f0b9/docs/rfcs/0001-kubernetes-execution-backend.md
[lody]: https://github.com/LodyAI/Lody/tree/d3179e1f7538b61d0a6acc6be0a324281be4e3c0
[agentkit]: https://github.com/danielkov/rust-sdk/tree/08355e7086a715be0a26b151d92f7c0812adda5d
[mango]: https://github.com/juliopolycarpo/mango-external-agents/blob/7b6bd40917f3d7275cbf2145f2970290e67bb3a0/docs/harness-acp.md
