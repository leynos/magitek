# Magitek

_A planned bounded async Agent Client Protocol client for Rust._

Magitek proposes a shared client for applications that run coding agents over
the [Agent Client Protocol (ACP)][acp]. Its contract covers resource admission,
ordered event delivery, deadlines, and explicit failure outcomes. Reusable
framing and accounting primitives form a separate layer for other protocol
roles, including Podbot's proxy.

**Status: tooling baseline.** This repository contains the project
documentation and a dependency-free Rust library scaffold with formatting,
lint, test, coverage, and CI entry points. The ACP protocol, host API, and
runtime are not implemented, so there is no protocol behaviour to install or
run. Dependency selection, the public API, and release packaging remain open
qualification decisions.

______________________________________________________________________

## Why Magitek?

An async API says when work can wait. It doesn't say how much work may wait. A
bounded channel also provides little protection when the next component accepts
everything into an unbounded queue.

The proposed contract follows retained work across those boundaries. It counts
frames, bytes, outstanding requests, callbacks, and waiting producers, and
defines what happens when each budget runs out. A slow consumer must produce an
observable overload outcome without accumulating unlimited work or silently
discarding transcript updates.

The initial consumers have different responsibilities. The planned Rust Lody
daemon needs an ACP client whose callbacks cannot monopolize its control loop.
Podbot needs framing and accounting that its policy proxy can reuse while
preserving the proxy's own authority and message-forwarding rules. The
[terms of reference][terms] define the shared requirement and its limits.

______________________________________________________________________

## Start with the design

The current entry point is documentation review:

1. Read the [terms of reference][terms] for the problem, scope, and success
   criteria.
2. Read the [context][context] for the source evidence and existing library
   candidates.
3. Review the [design][design] for ownership, admission, ordering, and failure
   contracts.
4. Use the [roadmap][roadmap] to follow qualification and implementation work.

The first dependency decision must compare the official Rust ACP SDK,
Agentkit's bounded SDK fork, and Mango's client and transport work against the
same requirements. The context document records their source baselines and
known gaps. Existing bounded implementations are candidates for reuse; the
choice needs evidence from the required failure cases.

Beneath that protocol engine, Magitek plans to obtain resource budgeting and
stream parsing from [Wireframe][wireframe]. The Wireframe work that delivers
those primitives is still proposed, so the [roadmap][roadmap] names the
Wireframe task that blocks each Magitek task. [ADR 0001][adr-0001] records the
decision.

______________________________________________________________________

## Proposed capabilities

The design specifies these capabilities. None represents shipped behaviour.

- **Bounded framing.** Enforce message-size limits while reading, before an
  arbitrary line becomes a complete allocation. Account for queued and
  in-flight data in both directions.
- **Admission with ownership.** Retain resource reservations through internal
  handoffs. Bound requests, host callbacks, and waiting producers as well as
  the visible message queues.
- **Progress under pressure.** Reserve capacity for necessary control traffic
  and keep expensive host work outside ordered protocol dispatch. Define a
  terminal failure when the transport cannot make progress within its budget.
- **Ordered, faithful delivery.** Preserve required ACP content and event
  ordering. Expose terminal results only after preceding events reach the
  contract's delivery boundary; let the host define durable persistence.
- **Explicit uncertainty.** Distinguish work rejected before submission from
  work whose delivery becomes uncertain. Keep request cancellation, session
  cancellation, transport closure, and process termination separate.
- **Inspectable operation.** Report queue occupancy, retained bytes, queue age,
  outstanding work, and failure causes through bounded diagnostic paths.

These budgets cover resources the library owns. The design must state the
accounting boundary for decoded values, host-retained data, and transport
buffers. It cannot promise a hard limit on the host application's memory or
make an unresponsive peer answer.

______________________________________________________________________

## Ownership boundaries

Magitek's proposed client owns ACP interaction within one connection. Its host
owns the environment and the consequences of agent work.

| Responsibility                                             | Proposed owner                  |
| ---------------------------------------------------------- | ------------------------------- |
| ACP negotiation, correlation, event order, and admission   | Magitek client                  |
| Framing and resource-reservation primitives                | Wireframe, via Magitek adapters |
| Proxy inspection, authorization, and forwarding policy     | Podbot                          |
| Process launch, placement, termination, and restart        | Host                            |
| Filesystem authority and permission decisions              | Host                            |
| Command journals, durable history, Loro sync, and recovery | Host                            |
| Ishiban work-item identity and workflow state              | Ishiban and its adapters        |

_Table 1: Proposed responsibility boundaries._

This keeps process placement and durable storage replaceable without putting
their work on the protocol dispatcher. A local subprocess, a container, and a
remote agent need qualified adapters; sharing an interface alone does not
establish equivalent lifecycle or recovery guarantees.

______________________________________________________________________

## Develop

The library scaffold carries the shared build spine. Install the pinned
toolchain and linkers, then run the checks:

```sh
make install-build-tools
make all typecheck
```

`make all` covers formatting, lint, tests, tooling integration, shared workflow
contracts, and spelling; `make typecheck` adds the compiler check.
`make coverage` writes an LCOV report. The [developer guide][developers] lists
prerequisites, test lanes, coverage commands, and CI administration.

______________________________________________________________________

## Learn more

- [Documentation contents][contents] – the complete documentation index.
- [Developer guide][developers] – local commands, test lanes, and CI.
- [Terms of reference][terms] – purpose, stakeholders, scope, and constraints.
- [Context][context] – source evidence, integration needs, and alternatives.
- [Design][design] – proposed architecture and operational contracts.
- [Roadmap][roadmap] – delivery work, dependencies, and acceptance criteria.

______________________________________________________________________

## Licence

The project has not selected a licence. No `LICENSE` file accompanies this
proposal. Licence selection is required before a software release.

______________________________________________________________________

## Contributing

Review the contracts and challenge them with concrete failure cases. Useful
feedback identifies a retaining owner that escapes its budget, a callback that
can block protocol progress, an ordering guarantee that fails during shutdown,
or an existing implementation that already satisfies the requirement.

Keep implementation proposals tied to the [roadmap][roadmap]. Include source
versions and reproducible traces when reporting compatibility findings.

[acp]: https://agentclientprotocol.com/
[contents]: docs/contents.md
[developers]: docs/developers-guide.md
[terms]: docs/terms-of-reference.md
[context]: docs/context.md
[design]: docs/magitek-design.md
[roadmap]: docs/roadmap.md
[wireframe]: https://github.com/leynos/wireframe
[adr-0001]: docs/adrs/adr-0001-reuse-wireframe-for-budgeting-and-stream-parsing.md
