# Architectural decision record (ADR) 0001: Reuse Wireframe for budgeting and stream parsing

## Status

Accepted (2026-11-19). Magitek plans to build its resource accounting and its
byte-stream framing, bounded decoding, and bounded encoding on Wireframe's
native-protocol primitives. Adoption of each capability waits for the Wireframe
roadmap task that delivers it and for Magitek's own qualification of a pinned
Wireframe revision. No Wireframe dependency exists in `Cargo.toml` yet.

## Date

2026-11-19.

## Context and problem statement

The [technical design](../magitek-design.md) requires admission before
allocation, charges that follow retained data, partition-invariant framing, and
byte-preserving inspection for a proxy. The draft of 2026-11-14 assumed that
Magitek would implement those mechanisms in its own transport and admission
modules, beneath whichever Agent Client Protocol (ACP) engine passed the
foundation gate.

Wireframe has since extended its proposed native-protocol contracts to cover
that requirement set.[^1] Requests for Comments (RFCs) 0003–0008 and roadmap
step 21.8 name Magitek as a standalone bounded consumer, and require the
primitives to work without Wireframe's server router, default envelope, or an
embedded ACP engine.[^2] These RFCs have the status "proposed", and every task
in Wireframe roadmap phase 21 remains unchecked at the inspected revision. They
describe intended behaviour, not a shipped capability.

Two separately maintained implementations of the same reservation ledger and
delimiter framer would duplicate the hardest verification work in both
repositories. The question is which mechanisms Magitek obtains from Wireframe,
which it retains, and what gates the dependency.

## Decision drivers

- Avoid a second budget library and a second bounded framer with independent
  defects and proof obligations.
- Keep ACP semantics, session-event watermarks, permissions, and delivery
  evidence in Magitek, where the design assigns them.
- Preserve one writer and one semantic correlation owner per connection.
- Keep every claimed bound traceable to an enforcement point in a pinned
  revision, including the revisions of dependencies.
- Keep the sequencing cost of an external pre-1.0 dependency visible.

## Options considered

### Option A: Implement framing and accounting inside Magitek

Magitek keeps full control of scheduling and has no external gate. It must
design, test, and model its own reservation kernel, ownership transfer,
delimiter framing, and bounded encoder, repeating work that Wireframe's roadmap
already carries for the same requirements.

### Option B: Reuse Wireframe for budgeting and stream parsing

Magitek consumes Wireframe's policy validation, reservation and
ownership-transfer primitives, delimiter framing with its newline-delimited
JSON (JSONL) profile, and admitted decoding and bounded encoding. Magitek
supplies the ACP-specific policy, the JSON adapter's profile choices, and all
session semantics. The ACP engine decision remains with the foundation gate.

### Option C: Adopt the complete Wireframe connection runtime now

Magitek would also commit to Wireframe's duplex session driver and supplied
transport entry points before the foundation gate compares engines. This
pre-empts that gate: the official software development kit (SDK), Agentkit, and
Mango each bring a dispatch loop, and RFC 0004 forbids competing dispatch loops
on one connection.

| Topic                         | Option A         | Option B                                | Option C                    |
| ----------------------------- | ---------------- | --------------------------------------- | --------------------------- |
| Duplicated verification       | High             | Low                                     | Low                         |
| External sequencing gate      | None             | Wireframe 21.8.1–21.8.4, 21.8.8–21.8.10 | Wireframe 21.8.1–21.8.10    |
| Foundation gate preserved     | Yes              | Yes                                     | No                          |
| Shared primitive for a proxy  | Magitek-specific | Shared with other consumers             | Shared with other consumers |
| Exposure to pre-1.0 API churn | None             | Framing and accounting surfaces         | Entire connection lifecycle |

_Table 1: Comparison of the framing and accounting options._

## Decision outcome / proposed direction

Choose option B. Magitek plans to use Wireframe for two concerns:

- **Budgeting:** immutable policy validation, atomic multi-scope reservations,
  charged ownership transfer, bounded first-in, first-out admission, and
  generation retirement (Wireframe RFC 0007; roadmap tasks 21.8.1, 21.2.1, and
  21.8.2).
- **Stream parsing:** bounded delimiter framing with the raw JSONL profile,
  admitted semantic decoding, and bounded encoding (Wireframe RFCs 0003 and
  0006; roadmap tasks 21.8.3 and 21.8.4), plus byte-preserving enforced proxy
  inspection (roadmap task 21.8.8).

Wireframe's duplex session driver and supplied transport entry points (RFCs
0004 and 0005; roadmap tasks 21.8.5 and 21.8.6) are not adopted by this
decision. They become a candidate within the foundation gate: the "narrow
dispatcher using official schema types" option runs on that driver instead of
on a dispatcher written from nothing. The foundation decision record selects or
rejects it on the same evidence as the other engines.

[Design §3.3](../magitek-design.md#33-wireframe-reuse-and-adoption-gates) maps
each mechanism to its Wireframe contract and gating task. The
[roadmap](../roadmap.md) records the blocking Wireframe task against each
Magitek task. [Wireframe issue 929][wireframe-adoption-issue] sets out the
corresponding pathway and open issues in Wireframe.

## Goals and non-goals

- Goals:
  - Obtain reservation, framing, decoding, and encoding mechanisms from one
    shared implementation whose bounds Magitek can audit.
  - State, per Magitek task, which Wireframe task must be delivered first.
  - Keep Wireframe types inside Magitek's transport and admission modules, so
    that ACP session logic depends on Magitek-owned types.
- Non-goals:
  - Adopting Wireframe's server application, router, middleware, default
    envelope, serializer, connection pool, or push registry.
  - Moving ACP session state, permission policy, event watermarks, delivery
    evidence, or durability into Wireframe.
  - Selecting the ACP engine. Roadmap step 1.2 still makes that decision.
  - Treating Wireframe's test harness (Wireframe roadmap task 21.1.3) as a
    gate. Magitek may reuse it where a pinned revision supplies it.

## Migration plan

No runtime code exists, so nothing migrates. Adoption proceeds as follows:

1. Record the dependency and its gates in the design and roadmap (this
   change).
2. When Wireframe task 21.8.1 is delivered, add the Wireframe dependency and
   qualify the selected version for policy validation before Magitek roadmap
   task 1.1.2 starts. Use an exact Git revision while no published release
   contains the required interfaces. Once a release does, require that exact
   version with an `=` requirement, so that a downstream consumer cannot
   resolve an unqualified release. That requirement is a documented exception
   to the workspace caret rule (AGENTS.md): the foundation decision (Magitek
   roadmap task 1.2.6) records the exception and the qualified version before a
   published release replaces the Git revision, and the exception is revisited
   when Wireframe reaches 1.0. A caret requirement may replace it only when
   every version it permits has a qualification record.
3. Qualify the selected version beneath the shared conformance exchange, with
   an ownership map across every handoff between Wireframe and the candidate
   engine (Magitek roadmap task 1.2.5). This completes the full qualification
   after task 1.1.2 has converted a validated policy into a Wireframe profile.
4. Re-run the ownership and compatibility corpus on every Wireframe version
   change, and change the pinned revision or exact requirement only together
   with its qualification record (Magitek roadmap task 4.4.2). The release
   matrix and compatibility statement name the qualified version, so a consumer
   can check the version its own lockfile resolves before relying on the
   advertised profile.

## Known risks and limitations

- **Sequencing.** Only Magitek roadmap tasks 1.1.3 and 1.2.1 can start before
  Wireframe delivers task 21.8.1. Every other open task depends, directly or
  transitively, on a Wireframe task that is unchecked at the inspected revision.
- **Proposed contracts.** The Wireframe RFCs are proposals. A change to a
  proposed contract can invalidate a mapping in design §3.3. Each pin therefore
  needs its own qualification record.
- **Pre-1.0 interfaces.** Wireframe 0.3.0 predates the phase 21 interfaces, and
  Wireframe's roadmap states that pre-1.0 interfaces may be replaced. No
  Wireframe roadmap task yet commits to a release that contains them.
- **Downstream resolution.** A caret requirement would let a consumer's own
  lockfile select an unqualified Wireframe release. The exact requirement in
  step 2 removes that exposure, but it can conflict with another dependency
  that needs a different Wireframe version. No other published crate is known
  to depend on Wireframe; task 4.4.2 revisits the requirement when such a
  consumer or a 1.0 release appears.
- **Hidden handoffs.** Wireframe's checks cannot meter an engine's internal
  queues or arbitrary callback allocations. A bounded Wireframe layer beneath
  an unbounded SDK path does not satisfy goal G1.
- **Double parsing.** An engine that insists on reading and parsing its own
  lines would repeat admitted work outside the ledger. Qualification must show
  the selected engine accepts admitted frames without an uncharged re-read.

If Wireframe withdraws or materially weakens a gating contract, the affected
Magitek tasks stay blocked. Implementing a private replacement requires an ADR
that supersedes this one; a silent fallback is not permitted.

## Outstanding decisions

- Whether `EventLease` embeds a Wireframe ownership guard directly or holds it
  behind a Magitek-owned ledger port. Magitek roadmap task 2.1.1 decides this
  from the delivered interface.
- Whether a Podbot proxy consumes the primitives through a Magitek facade that
  carries the ACP profile choices, or depends on Wireframe directly. Magitek
  roadmap task 4.1.1 decides this.
- Whether the foundation gate selects Wireframe's duplex session driver.
  Magitek roadmap task 1.2.6 records that decision.

## Architectural rationale

The design separates domain policy from transport, process, and telemetry
adapters. Framing and reservation accounting are protocol-neutral mechanisms;
ACP negotiation, ordering evidence, and failure classification are Magitek's
domain. Placing the mechanisms in a shared library, and the policy that
configures them in Magitek, follows that separation. It also gives Podbot's
proxy and the full client the same enforcement primitive, which goal G5
requires.

[^1]: Wireframe pull request [917][wireframe-pr-917], merged on 2026-11-18.
[^2]: Wireframe at `052065fa61cfc93d730f8a75a794da1a959dc2ca`, inspected on
    2026-11-19: [roadmap step 21.8][wireframe-roadmap-21-8] and
    [RFC 0008's mandatory ACP profile][wireframe-rfc-0008-acp].

[wireframe-pr-917]: https://github.com/leynos/wireframe/pull/917
[wireframe-roadmap-21-8]: https://github.com/leynos/wireframe/blob/052065fa61cfc93d730f8a75a794da1a959dc2ca/docs/roadmap.md#218-qualify-bounded-standalone-consumers-with-acp
[wireframe-rfc-0008-acp]: https://github.com/leynos/wireframe/blob/052065fa61cfc93d730f8a75a794da1a959dc2ca/docs/rfcs/rfc-0008-external-adapter-conformance-harness.md#mandatory-acp-v1-and-jsonl-toy
[wireframe-adoption-issue]: https://github.com/leynos/wireframe/issues/929
