# Architectural decision record (ADR) 0002: Support application-owned ACP host ports

## Status

Proposed. This decision extends the contract-work sequencing in ADR 0001 while
preserving every Wireframe runtime adoption and qualification gate.

## Date

2026-11-20.

## Context and problem statement

Youxia needs to develop its `youxiad` daemon and `arun` process transport
before Magitek delivers its qualified runtime. Coupling the daemon's
application logic to the official Agent Client Protocol (ACP) software
development kit (SDK) would make later adoption depend on SDK-specific types
and failure semantics. Waiting for all Magitek runtime gates would also
postpone feedback about the host boundary.

Magitek already separates the host's process, policy, and durability ownership
from its protocol client. Its proposed delivery evidence, ordered events, and
generation rules define the target semantics. The consuming application's port
must preserve those meanings without claiming that a provisional SDK path has
passed Magitek's resource qualification.[^1]

## Decision drivers

- Develop the host and raw process transport independently of the ACP engine.
- Keep capability absence observable without weakening required correctness.
- Reuse one consumer contract and fixture corpus across adapter changes.
- Preserve Magitek's general library boundary and Wireframe adoption gates.

## Options considered

1. **Expose the official SDK throughout the host.** This accelerates the first
   exchange but lets engine types and behaviour define application contracts.
2. **Wait for Magitek's runtime before integrating the host.** This avoids a
   provisional adapter but delays process and persistence feedback that does
   not depend on qualified resource accounting.
3. **Let the application own a port with explicit adapter profiles.** The host
   can develop against an experimental SDK adapter, and later qualify a Magitek
   adapter against the same observable semantics.

## Decision outcome / proposed direction

Choose option 3. Youxia owns `AcpHostPort` and the `acpsdk` and `magitek`
adapters, initially as modules. Magitek exposes its general facade and reusable
evidence contracts. The library does not depend on Youxia or `arun`, and the
application domain does not depend on either engine's concrete types. The
[Youxia port contract][youxia-port] governs its consuming API;
[design §10.4](../magitek-design.md#104-application-owned-acp-host-ports)
governs the Magitek integration boundary.

Capability profiles distinguish implementation support, peer negotiation,
installed host services, current policy/readiness, and qualification. An
optional operation may fail with an explicit reason. Every successful outcome
must still preserve submission evidence, generation authority, and event
completeness. An experimental profile may disclose unqualified resource paths;
it cannot claim bounded hosting or silently weaken a requested guarantee.

Select an adapter at protocol-generation construction. Replace it for fresh
generations and new runs after conformance qualification. The initial design
does not transfer active engine state or restore lost ACP correlation state
after a daemon crash. `arun` remains a raw transport and process owner under
the host's supervisor; it does not interpret ACP messages.

## Migration plan

1. Define the evidence and capability vocabulary and portable consumer
   fixtures in Magitek tasks 1.1.3, 1.1.4, 1.2.1, and 1.2.7. These tasks need
   no Wireframe runtime implementation. They extend ADR 0001's inventory of
   early contract work, not its implementation gates.
2. Develop Youxia's port, fake, raw `arun` transport, provisional SDK adapter,
   and experimental local loop through [Youxia roadmap step 1.5][youxia-spike].
   This external work neither selects Magitek's engine nor completes Magitek
   task 1.2.2 or its later qualification tasks.
3. Complete Magitek's existing foundation, resource, event, and host-service
   gates. Tasks 4.2.1–4.2.3 then qualify the downstream Magitek adapter with
   the shared consumer fixtures and a real Youxia/`arun` integration. Record
   the exact adapter, engine, schema, Wireframe, and host revisions.

The same conformance cases must reject unsupported calls before publication,
preserve an update prefix before completion, distinguish cancellation from
process exit, and fence stale permission replies and uncertain operations. Real
adapter tests must supplement a fake's contract tests.

## Known risks and limitations

The provisional adapter may not expose enough internal SDK control to satisfy
all required semantics. Such a gap narrows the experiment or blocks the
operation; it does not justify a fabricated result. Passing consumer semantics
does not establish Magitek's resource bounds, and a bounded outer queue does
not establish bounds for retained SDK work.

Capability inventories can drift across repositories. Keep Youxia's port
normative for its application and use versioned fixture records to identify the
subset a Magitek release can implement. Do not publish a shared port crate
before a concrete consumer need justifies that package boundary.

## Outstanding decisions

- Fix the exact Rust surface and error representation through executable
  contract tasks; names in the design remain illustrative.
- Record the SDK profile's actual support and qualification gaps during the
  Youxia spike. This ADR does not assert an SDK capability matrix.
- Require a separate design and qualification before state migration between
  live engines or restoration of a crashed protocol driver.

[^1]: [Magitek design §§3 and 7–10](../magitek-design.md) defines the existing
    foundation, event, lifecycle, and interface contracts. Source inspections
    there do not establish a runtime qualification result.

[youxia-port]: https://github.com/leynos/youxia/blob/284127edaf6b78e9db7a504dc4215c7ac5ef016f/docs/contracts/acp-host-port.md
[youxia-spike]: https://github.com/leynos/youxia/blob/284127edaf6b78e9db7a504dc4215c7ac5ef016f/docs/roadmap.md#15-spike-the-local-agent-loop-through-an-acp-host-port
