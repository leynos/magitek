# Magitek roadmap

This roadmap implements goals G1–G6 in the
[terms of reference](terms-of-reference.md) through the proposed
[technical design](magitek-design.md). The
[context and evidence ledger](context.md) distinguishes inspected behaviour from
unverified assumptions. All tasks remain proposed; neither an unchecked task nor
a cited dependency establishes an implemented capability.

Goals, Ideas, Steps, and Tasks (GIST) organize the delivery sequence. Each phase
states a falsifiable idea, each step answers a delivery question, and each task
defines a review-sized execution unit. The roadmap makes no date commitments.
Unit, behavioural, and property checks accompany the implementation they verify;
dedicated end-to-end (E2E) tasks cover interactions that exceed one component.

The first release targets a bounded native client for stable Agent Client
Protocol (ACP) v1. Phase 4 qualifies actual host adoption; phase 5 contains
conditional extensions and does not gate that release. Ishiban's independent
observation milestone has no Magitek dependency. Podbot's proposed stream and
lifecycle interface is an explicit external adoption gate, while Kubernetes
support remains outside the initial release path.

## 1. Qualify the foundation and contract

Idea: a small executable contract and a source-backed engine qualification can
identify a viable bounded implementation before either host depends on its
public interface. The idea fails if every candidate requires hidden unbounded
work or unsupported protocol changes to complete the minimum exchange.

This phase establishes the build, fixtures, and decision evidence needed for the
first client. It does not declare an engine production-ready or treat source
inspection as a runtime result.

### 1.1. Make the proposed operating contract executable

Can one crate express the resource and failure contracts without acquiring host
responsibilities? The answer determines the interfaces exercised by the engine
qualification. See [magitek-design.md](magitek-design.md) §§1–5 and §10.

- [ ] 1.1.1. Establish the single-crate build and continuous integration spine.
  - Requires no earlier task.
  - See [magitek-design.md](magitek-design.md) §§4, 10, and 13.
  - Success: the supported native build, formatting, lint, and fixture checks
    run through documented commands; core dependencies exclude configuration
    loaders, storage engines, authentication clients, and container runtimes.
- [ ] 1.1.2. Implement immutable resource-policy validation.
  - Requires 1.1.1.
  - See [magitek-design.md](magitek-design.md) §5 and the
    [proposed policy schema](contracts/resource-policy.schema.json).
  - Success: structural and relational checks reject impossible reservations,
    arithmetic overflow, and disabled limits; generated boundary cases preserve
    those relationships, and host configuration converts into validated policy.
- [ ] 1.1.3. Define typed delivery evidence and terminal failure contracts.
  - Requires 1.1.1.
  - See [magitek-design.md](magitek-design.md) §§7–10.
  - Success: public types distinguish rejection before submission, uncertain
    submission, peer terminal evidence, transport closure, and process exit;
    compile-time examples cannot substitute a delivery watermark for durability.

### 1.2. Select an engine by its complete retained-work path

Can the preferred ACP implementation expose a path whose buffering and dispatch
ownership can be bounded? The qualification decides the engine, required patch
surface, and conditions that would force reconsideration. See
[magitek-design.md](magitek-design.md) §§3, 5–7, and 12–13.

- [ ] 1.2.1. Add the scripted peer and controllable byte-stream harness.
  - Requires 1.1.1.
  - See [magitek-design.md](magitek-design.md) §§6 and 12.
  - Success: fixtures can fragment reads, short-write output, stall either
    direction, advance test time, and disconnect at a chosen byte boundary;
    failures reproduce without network access or model inference.
- [ ] 1.2.2. Implement the official-SDK qualification exchange.
  - Requires 1.1.2, 1.1.3, and 1.2.1.
  - See [magitek-design.md](magitek-design.md) §§3, 7, and 12.
  - Success: the pinned official software development kit (SDK) initializes a
    session and exchanges a prompt, updates, and a result; an ownership map
    names every queue, task source, request map, session buffer, and retained
    payload on that path.
- [ ] 1.2.3. Qualify the Agentkit candidate against the shared exchange.
  - Requires 1.2.2.
  - See [magitek-design.md](magitek-design.md) §§3 and 12.
  - Success: the corpus covers the fork's charged transport and high-level
    session path at one pinned revision; the report identifies schema support
    and retained-work gaps. A failed must-pass condition has a minimal
    reproducer or source-backed rejection instead of an assumed workaround.
- [ ] 1.2.4. Qualify the reusable Mango peer against the shared exchange.
  - Requires 1.2.2.
  - See [magitek-design.md](magitek-design.md) §§3 and 12.
  - Success: the corpus exercises the lower-level peer separately from harness
    normalization; the report identifies fidelity, callback, and ownership
    limits. A failed must-pass condition has reproducible evidence, and branch
    evidence remains distinct from published-version evidence.
- [ ] 1.2.5. Record the qualified foundation and maintenance decision.
  - Requires 1.2.3 and 1.2.4.
  - See [magitek-design.md](magitek-design.md) §§3 and 13.
  - Success: an architectural decision record pins the engine and schema,
    identifies bounding work, selects property-test tooling and a provisional
    minimum Rust version, and states patch ownership and licence constraints.
    Upstream acceptance remains unassumed; a replacement engine requires a
    recorded decision. No unqualified path enters the advertised profile.

## 2. Deliver one bounded local ACP client

Idea: a native consumer can initialize one real ACP agent, submit one prompt,
and receive its ordered output through a bounded library-owned path. The idea
fails if a slow reader, large frame, or hidden engine queue defeats the declared
resource contract.

The first client uses supplied protocol streams and a host-owned runtime. It
advertises only implemented capabilities, and it can reject unsupported host
services while completing ordinary prompt exchanges.

### 2.1. Retain resource charges until ownership actually changes

Can admission account for queued, active, and consumer-held work without
creating unbounded waiting tasks? This step establishes the ownership rules used
by every later transport and callback. See
[magitek-design.md](magitek-design.md) §5.

- [ ] 2.1.1. Implement the resource ledger and charged event leases.
  - Requires 1.1.2 and 1.1.3.
  - See [magitek-design.md](magitek-design.md) §§5 and 7.
  - Success: count and byte charges follow retained work, including empty/null
    leases across close. Connection admission reserves control and terminal
    status storage; closed generations retain their connection slot until every
    obligation retires. Properties cover copies, transfers, and partial
    rollback.
- [ ] 2.1.2. Implement bounded asynchronous admission and cancellation.
  - Requires 2.1.1 and 1.2.1.
  - See [magitek-design.md](magitek-design.md) §§5 and 9.
  - Success: waiter count and data stay bounded under explicit first-in,
    first-out admission; timeout, cancellation, and close settle permits once.
    The finite FizzBee ownership model checks P1 conservation with the small
    state limits specified in design §12. Caller-retained input stays explicit.

### 2.2. Enforce limits before frames accumulate or expand

Can a connection reject oversized or expensive input before its representation
escapes accounting? The answer determines the supported frame profile and
parsing policy. See [magitek-design.md](magitek-design.md) §§5–6.

- [ ] 2.2.1. Implement the bounded newline-delimited frame decoder.
  - Requires 1.2.1 and 2.1.1.
  - See [magitek-design.md](magitek-design.md) §6.
  - Success: complete and fragmented oversized frames fail identically before
    excess retention; wire reservations include up to two delimiter bytes.
    Partial tails, text, and line endings have explicit dispositions; generated
    boundaries preserve decisions and trickles cannot reset the frame deadline.
- [ ] 2.2.2. Add structural accounting and admitted JSON processing.
  - Requires 1.2.5, 2.1.2, and 2.2.1.
  - See [magitek-design.md](magitek-design.md) §§4–6.
  - Success: nesting, nodes, decoded payloads, and work obey limits before
    materialization; duplicate keys and unsupported batches fail explicitly.
    The named processing deadline covers admitted decoder work without freeing
    live worker charges; bounded reorder state preserves ingress order. Fixtures
    expose structural expansion costs.
- [ ] 2.2.3. Implement a single bounded writer with submission evidence.
  - Requires 1.1.3, 2.1.2, and 2.2.2.
  - See [magitek-design.md](magitek-design.md) §§6 and 9.
  - Success: output retains charges through short writes and a deadline that
    includes queue time; possible transmission produces uncertainty. The
    encoder validates maximum control-envelope fit, including escaped IDs;
    reserved work never overtakes its causal prerequisite or a partial frame.

### 2.3. Drive the qualified engine without hidden dispatch growth

Can transport and response routing continue while application work is slow?
This step closes the engine-specific gaps and produces usable progress evidence
for the local consumer. See [magitek-design.md](magitek-design.md) §§4–7 and 11.

- [ ] 2.3.1. Route the selected engine through the audited bounded path.
  - Requires 1.2.5, 2.2.2, and 2.2.3.
  - See [magitek-design.md](magitek-design.md) §§3, 5, and 7.
  - Success: adapters preserve charges instead of pumping into an unbounded
    SDK queue; instrumentation covers internal session buffers and task
    sources. Any unsupported legacy route rejects bounded-mode construction
    explicitly.
- [ ] 2.3.2. Bound pending requests, session registrations, and retirement data.
  - Requires 2.3.1.
  - See [magitek-design.md](magitek-design.md) §§5, 7, and 9.
  - Success: admitted non-prompt requests have response deadlines; maps and
    parameters remain bounded. Generation-scoped IDs never repeat, including
    after timeout, while completed entries retire. Long generated sequences
    neither accumulate tombstones/routes nor let late replies revive operations.
- [ ] 2.3.3. Implement independent reader, writer, and dispatch progress rules.
  - Requires 2.3.2.
  - See [magitek-design.md](magitek-design.md) §§4, 6, and 7.
  - Success: ordered handlers perform bounded capture only; expensive work runs
    outside the driver. Saturation produces selective waiting or explicit
    closure under policy, without claiming to bypass an obstructed wire stream.
- [ ] 2.3.4. Expose bounded resource and progress diagnostics.
  - Requires 2.3.3.
  - See [magitek-design.md](magitek-design.md) §11.
  - Success: snapshots identify queue age, retained bytes, waiters, write and
    dispatch progress, and close reason; blocked exporters cannot stall the
    driver, labels have bounded cardinality, and payloads remain unlogged.

### 2.4. Complete a local prompt with honest event ordering

Can a native consumer observe all preceding session output before consuming its
completion watermark? This step supplies the first usable client and establishes
the distinction between delivery and persistence. See
[magitek-design.md](magitek-design.md) §§7–10 and 12.

- [ ] 2.4.1. Implement stable ACP v1 initialization, session creation, and
  prompting.
  - Requires 1.1.3 and 2.3.3.
  - See [magitek-design.md](magitek-design.md) §§8 and 10.
  - Success: initialization and non-prompt timers cover admission through
    response; capabilities match implemented methods and concurrent calls retain
    one active prompt per session. Admitted extension fields survive round trips
    or produce an explicit unsupported result.
- [ ] 2.4.2. Deliver charged session events and completion watermarks.
  - Requires 2.1.1 and 2.4.1.
  - See [magitek-design.md](magitek-design.md) §§7 and 10.
  - Success: the completion watermark names the required preceding sequence;
    the delivery watermark advances only through a contiguous yielded prefix.
    Public peer-result delivery waits for that prefix. Out-of-turn events retain
    session identity without invented turn provenance or durability evidence.
- [ ] 2.4.3. Expose terminal status independently from event consumption.
  - Requires 1.1.3, 2.3.4, and 2.4.2.
  - See [magitek-design.md](magitek-design.md) §§7, 9, and 11–12.
  - Success: a full event budget cannot hide failure, completeness, watermarks,
    or cleanup in the reserved status cell. A result observed before its prefix
    is yielded carries `delivery_pending`; unsupported updates mark an
    incomplete prefix, and reserved markers never fabricate a successful result.
- [ ] 2.4.4. Add the optional local-process adapter behind its feature boundary.
  - Requires 2.4.3.
  - See [magitek-design.md](magitek-design.md) §§4, 6, and 10.
  - Success: host-supplied launch and stop policy govern the child; stdout stays
    protocol-pure, bounded stderr drains independently, and observed process
    status uses its own channel. Enabling the adapter creates no hidden runtime
    and grants no process authority to the core or peer.
- [ ] 2.4.5. Add the native consumer E2E example and compatibility fixture.
  - Requires 2.4.4.
  - See [magitek-design.md](magitek-design.md) §§10 and 12.
  - Success: a documented consumer supplies a runtime, protocol streams, and
    separate lifecycle evidence to complete a prompt against a pinned real ACP
    agent. The scripted counterpart reproduces framing, event-consumer, and
    stderr-sink stalls; recorded output identifies checks requiring the real
    executable.

## 3. Deliver bounded host services and lifecycle semantics

Idea: adding permission, filesystem, and terminal requests can preserve bounded
protocol progress without obscuring cancellation or delivery uncertainty. The
idea fails if a delayed callback blocks response routing, widens authority, or
allows a stale reply to affect a replacement connection.

Host services remain explicit capabilities supplied by the embedding
application. This phase adds the lifecycle behaviour that both consumers need
before adopting the client for consequential agent work.

### 3.1. Serve agent requests through explicit bounded capabilities

Can host services remain responsive without performing host work on the protocol
driver? The result informs capability advertisement and the host integration
surface. See [magitek-design.md](magitek-design.md) §§4, 8, and 10.

- [ ] 3.1.1. Implement the bounded host-service request dispatcher.
  - Requires 2.1.2 and 2.3.3.
  - See [magitek-design.md](magitek-design.md) §§5, 7, and 8.
  - Success: callbacks reserve their response obligation before work starts;
    arguments, deadlines, and outstanding responders obey policy. Unavailable
    consumers fail explicitly; arbitrary host work never executes inside an
    ordered handler, and an over-limit reply uses bounded refusal or close.
- [ ] 3.1.2. Implement generation-fenced permission request handling.
  - Requires 3.1.1 and 2.4.1.
  - See [magitek-design.md](magitek-design.md) §§8–10.
  - Success: responses match offered choices and their original generation;
    expiry, duplicates, and replacement cannot grant authority. A person's
    response deadline starts at admission; its wait holds no CPU worker.
    Properties cover reply-versus-cancel and reply-versus-close races.
- [ ] 3.1.3. Implement bounded filesystem service dispatch and replies.
  - Requires 3.1.1.
  - See [magitek-design.md](magitek-design.md) §§8 and 10.
  - Success: file requests and returned content fit declared limits; capability
    advertisement follows the supplied implementation; the host retains path
    policy and filesystem authority, including refusal of unsupported requests.
- [ ] 3.1.4. Implement bounded terminal service dispatch and retained output.
  - Requires 3.1.1.
  - See [magitek-design.md](magitek-design.md) §§5, 8, and 10.
  - Success: terminal handles, output, waits, and releases have finite budgets;
    lifecycle evidence remains distinct from ACP prompt completion; fixtures
    exercise output limits, missing handles, and close during a terminal wait.
- [ ] 3.1.5. Add the independent typed authentication broker.
  - Requires 3.1.1 and 3.1.2.
  - See [magitek-design.md](magitek-design.md) §§2, 8, and 10.
  - Success: exchanges use peer-advertised methods and host-supplied handling;
    authentication cannot grant permission or acquire filesystem authority.
    Expiry and connection replacement fence the exchange, while credentials and
    browser or cloud login remain host responsibilities.

### 3.2. Preserve uncertainty through cancellation and replacement

Can a caller stop waiting, request cancellation, or replace transport without
inventing evidence that work stopped? This step defines safe recovery inputs for
host-owned journals and supervisors. See [magitek-design.md](magitek-design.md)
§§8–10.

- [ ] 3.2.1. Implement request cancellation and prompt cancellation separately.
  - Requires 2.2.3, 2.3.2, and 2.4.2.
  - See [magitek-design.md](magitek-design.md) §§8–9.
  - Success: drop, withdrawal, cancellation intent, and peer stop reason remain
    distinct. Extend the FizzBee model over the atomic publication/cancel
    transition for P3; partial-write faults preserve uncertainty and no process
    exit is inferred. Prompt computation has no short generic request timeout;
    a host turn budget remains explicit.
- [ ] 3.2.2. Implement explicit close and selective-stall termination.
  - Requires 3.1.1 and 3.2.1.
  - See [magitek-design.md](magitek-design.md) §§6, 9, and 11.
  - Success: write, dispatch, callback, and consumer stalls produce distinct
    bounded outcomes; close settles waiters and pending calls once. Extend the
    same FizzBee model through close/cancel; retained leases and running workers
    remain charged, with incomplete cleanup visible independently of events.
- [ ] 3.2.3. Add explicit session loading and generation-safe reconnection.
  - Requires 3.1.2 and 3.2.2.
  - See [magitek-design.md](magitek-design.md) §§8–10.
  - Success: loading follows negotiated agent support; replacement invalidates
    stale requests and responders; the API exposes unresolved submissions and
    never replays a prompt automatically. Host reconciliation remains explicit.

### 3.3. Exercise bilateral progress and capability interactions

Do the client and service contracts still hold when both directions saturate?
The resulting E2E evidence determines whether the library can enter host
adoption without hiding protocol deadlocks. See
[magitek-design.md](magitek-design.md) §12.

- [ ] 3.3.1. Add the bilateral-overload and cancellation E2E suite.
  - Requires 2.3.4, 3.1.2, and 3.2.3.
  - See [magitek-design.md](magitek-design.md) §§6–9 and 12.
  - Success: update floods, held leases, permission requests, partial writes,
    and cancellation interact under one deterministic run; each scenario either
    preserves progress within policy or terminates explicitly without event loss
    disguised as successful completion.
- [ ] 3.3.2. Add host-capability and lifecycle combination qualification.
  - Requires 2.4.5, 3.1.3, 3.1.4, 3.1.5, and 3.3.1.
  - See [magitek-design.md](magitek-design.md) §§8, 10, and 12.
  - Success: the declared capability combinations exercise unsupported methods,
    callback timeout, terminal exit, authentication, and transport replacement;
    diagnostics distinguish peer silence from a held host handler. Mandatory
    faults precede pairwise remainder coverage; a pinned real agent qualifies
    the profile, and unavailable cases never count as passes.

## 4. Integrate hosts and qualify release under contention

Idea: Podbot and the native Lody host can adopt the same bounded contract while
retaining their own process, policy, and persistence responsibilities. The idea
fails if either integration needs unbounded side queues, a duplicated ACP
engine, or a claim stronger than the library's actual delivery evidence.

This phase requires real integration evidence before release. A mock stream
adapter can develop the seam but cannot satisfy Podbot adoption. The native Lody
host and Podbot's usable stream interface are external dependencies; their
availability must be recorded, not assumed from a design proposal.

### 4.1. Reuse framing and accounting in an enforced Podbot proxy

Can Podbot use the shared primitives while remaining a protocol proxy? The
answer validates the extraction boundary and determines the minimum downstream
change. See [magitek-design.md](magitek-design.md) §§6, 10, and 13.

- [ ] 4.1.1. Expose byte-preserving inspection with bounded policy decisions.
  - Requires 2.2.2 and 3.2.2.
  - See [magitek-design.md](magitek-design.md) §§6 and 10.
  - Success: an enforced proxy can inspect admitted frames while forwarding
    allowed bytes unchanged; unsupported or oversized input closes under policy
    and never switches to raw forwarding. Extension content remains intact.
- [ ] 4.1.2. Qualify the real Podbot protocol-stream and lifecycle seam.
  - Requires 2.4.5 and 4.1.1.
  - See [magitek-design.md](magitek-design.md) §§10 and 13.
  - Success: a native Magitek consumer completes a prompt through pinned real
    Podbot streams and separate lifecycle status; protocol stdout and diagnostic
    stderr drain independently. Hook-control traffic has separate bounds and
    never enters agent stdin. The proposed Podbot API remains an external gate
    until implemented; mocks do not pass it.
- [ ] 4.1.3. Integrate the qualified primitives into Podbot's enforcement path.
  - Requires 4.1.2 and 3.3.2.
  - See [magitek-design.md](magitek-design.md) §§2, 10, and 13.
  - Success: the integration retains Podbot's capability masking, workspace
    policy, process ownership, and cleanup; no core container dependency or
    adapter dependency cycle appears. Limits cover adapter and core buffers.
- [ ] 4.1.4. Add the real Podbot policy and framing E2E suite.
  - Requires 4.1.3.
  - See [magitek-design.md](magitek-design.md) §§6, 10, and 12.
  - Success: allow/deny policy, initialization rewriting, malformed input,
    complete and fragmented oversized frames, and close during inspection
    preserve the enforcement boundary; tests verify allowed bytes and extension
    fields without accepting overflow as a policy bypass.

### 4.2. Integrate the native Lody host without owning durability

Can Lody map command and history durability onto Magitek's explicit evidence
without slowing the connection driver? This step validates the client use case
and keeps the Ishiban observation milestone independent. See
[magitek-design.md](magitek-design.md) §§7, 9–10, and 13.

- [ ] 4.2.1. Implement the native-host command admission adapter.
  - Requires 3.2.3 and 3.3.2.
  - See [magitek-design.md](magitek-design.md) §§9–10.
  - Success: a host-owned durable command record precedes submission; the
    adapter records rejection, known result, or unknown outcome without blind
    replay. The native host's journal interface is an explicit external gate;
    Magitek imports no storage or authentication implementation.
- [ ] 4.2.2. Integrate incremental history consumption through charged events.
  - Requires 4.2.1 and 2.4.2.
  - See [magitek-design.md](magitek-design.md) §§5, 7, and 10.
  - Success: host workers transfer charges under a bounded budget and apply
    incremental history; the terminal projection waits for the required durable
    prefix. Slow storage and disk exhaustion cannot create an unbounded queue,
    move replication onto the driver, or report false durable success.
- [ ] 4.2.3. Add the real native-host dispatch and history E2E qualification.
  - Requires 4.2.2 and 3.3.2.
  - See [magitek-design.md](magitek-design.md) §§9–10 and 12.
  - Success: a pinned native host and real ACP agent preserve command
    uncertainty and history ordering through disconnect and restart; an
    independent local reader verifies the declared intent and history records.
    Cloud catalogue and peer-convergence checks stay in the daemon's roadmap.

### 4.3. Preserve declared budgets under shared-host contention

Do independent connections remain within their combined allocation when one
agent or consumer dominates traffic? These results determine the supported load
profile and expose host scheduling assumptions. See
[magitek-design.md](magitek-design.md) §§4–5 and 11–12.

- [ ] 4.3.1. Implement fair service across the shared host budget.
  - Requires 2.1.2, 2.3.4, and 3.3.1.
  - See [magitek-design.md](magitek-design.md) §§4–5 and 10–11.
  - Success: ready connections receive round-robin service with finite work
    batches; no connection consumes another's control reserve. Contention and
    cancellation preserve charges and waiter order; retained closed generations
    count against connection capacity. No agent-placement responsibility enters
    the shared scheduler.
- [ ] 4.3.2. Run the combined saturation and soak qualification.
  - Requires 4.1.4, 4.2.3, and 4.3.1.
  - See [magitek-design.md](magitek-design.md) §§11–12.
  - Success: the proposed design §12.3 workload and every mandatory §12.2
    combination have recorded results, including quiet-connection progress,
    lifetime churn, and retained empty/null leases. Reports name CPU service and
    distinguish charged resources, resident memory, delay, and termination;
    failures remain visible and force review of the advertised profile.

### 4.4. Release a contract that consumers can reproduce

Can a consumer reproduce the qualified profile and understand its limits without
reading engine internals? This step makes compatibility, migration, and
operating evidence part of the release decision. See
[magitek-design.md](magitek-design.md) §§11–13.

- [ ] 4.4.1. Publish executable consumer guidance and failure interpretation.
  - Requires 3.3.2, 4.1.3, and 4.2.2.
  - See [magitek-design.md](magitek-design.md) §§9–11 and 13.
  - Success: examples exercise the shipped API; documentation covers policy
    validation, event lease ownership, callback authority, lifecycle evidence,
    overload, and uncertain outcomes. Examples do not imply durable acceptance
    or recovery behaviour supplied only by a host.
- [ ] 4.4.2. Establish the engine-upgrade and compatibility regression gate.
  - Requires 1.2.5, 3.3.2, 4.1.4, and 4.2.3.
  - See [magitek-design.md](magitek-design.md) §§3, 12, and 13.
  - Success: the release matrix pins protocol, engine, schema, agents, hosts,
    and feature profiles; an engine change reruns relevant ownership and E2E
    checks. Fork patches, licences, unsupported paths, and rollback constraints
    remain inspectable.
- [ ] 4.4.3. Record the release licence and supported implementation profile.
  - Requires 1.2.5, 2.4.5, and 4.4.2.
  - See [magitek-design.md](magitek-design.md) §§3, 12, and 13.
  - Success: maintainers choose a dependency-compatible licence, minimum Rust
    version, runtime and platform profile, feature support, and API versioning
    policy. The record names tested combinations without implying that this
    documentation proposal already ships a library.
- [ ] 4.4.4. Produce the first release candidate and its qualification record.
  - Requires 4.3.2, 4.4.1, and 4.4.3.
  - See [magitek-design.md](magitek-design.md) §§1, 12, and 13.
  - Success: the candidate's documented promises match recorded evidence;
    unresolved defects and unsupported profiles remain visible; both actual host
    integrations pass their gates. No task in phase 5 is a release prerequisite.

## 5. Evaluate deferred capabilities only when demanded

Idea: a qualified core contract can accommodate a requested extension without
weakening existing bounds or forcing unrelated consumers to adopt new host
dependencies. The idea fails when an extension needs a different promise that
cannot remain isolated behind a separately qualified profile.

These tasks activate only for a concrete consumer requirement. Their presence
records a decision path, not a commitment to broaden the first release.

### 5.1. Qualify additional transport and execution environments

Can a requested environment preserve the existing stream, lifecycle, and
resource contracts? The outcome determines whether it belongs in a host adapter
or needs a separately reviewed protocol profile. See
[magitek-design.md](magitek-design.md) §§10 and 13.

- [ ] 5.1.1. Qualify a demanded remote transport adapter.
  - Requires 4.4.4.
  - See [magitek-design.md](magitek-design.md) §§6, 9–10, and 13.
  - Success: the adapter declares authentication ownership, framing, closure,
    reconnect, and resource limits; its E2E evidence preserves uncertainty and
    excludes automatic prompt replay. Container or Kubernetes placement remains
    the execution host's responsibility.
- [ ] 5.1.2. Qualify a demanded additional native platform.
  - Requires 4.4.4.
  - See [magitek-design.md](magitek-design.md) §§4, 10, and 13.
  - Success: platform-specific stream, termination, stderr, and lifecycle
    behaviour pass the relevant consumer suites; the support matrix records
    actual results without making that platform a prerequisite for the initial
    native release.

### 5.2. Admit a later protocol profile through independent evidence

Can a requested protocol revision preserve the published resource and evidence
contracts? The answer determines versioned API boundaries rather than silently
changing the stable ACP v1 profile. See
[magitek-design.md](magitek-design.md) §§3 and 13.

- [ ] 5.2.1. Prototype a demanded ACP revision against the conformance harness.
  - Requires 4.4.4.
  - See [magitek-design.md](magitek-design.md) §§3, 7–10, and 13.
  - Success: one representative session exchange exercises changed ordering,
    lifecycle, or capability semantics; a recorded decision identifies remaining
    compatibility work as review-sized tasks before production adoption. The
    stable ACP v1 regression gate continues to pass.

### 5.3. Change packaging only when consumer evidence requires it

Would separating reusable primitives reduce measured integration cost without
splitting the operating contract? This step keeps packaging responsive to actual
adoption. See [magitek-design.md](magitek-design.md) §§4, 10, and 13.

- [ ] 5.3.1. Qualify a consumer-driven package or feature split.
  - Requires 4.4.4.
  - See [magitek-design.md](magitek-design.md) §§4, 10, and 13.
  - Success: an architectural decision record identifies the concrete consumer
    benefit, migration path, and preserved ownership boundaries; existing host
    and compatibility suites still exercise every advertised bounded profile.
