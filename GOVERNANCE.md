# Governance model

Anubis separates judgment from enforcement.

The reviewer reduces, falsifies, measures, simulates, and weighs. The Python
gate validates the packet and verdict, checks authority and reproducibility,
rejects unresolved contradictions or conditions, and emits the passage result.
Neither layer may silently expand the other.

## Roles

- **Proposer:** defines the claim and requested action.
- **Packet builder:** gathers bounded evidence and records provenance.
- **Authority holder:** confirms the actor and scope; this cannot be inferred.
- **Anubis reviewer:** issues one closed verdict without repairing the proposal.
- **Mechanical gate:** decides passage from validated inputs.
- **Executor:** acts only after passage and only within independently granted
  authority.

One person or agent may technically occupy multiple roles, but self-review
weakens the independence claim and must be disclosed. Anubis may never approve
changes to its own gate in the same review that proposes those changes.

## Accepted risk

Known risk is not the same as undiscovered failure. An accepted-risk entry must
name the risk, accepting authority, bounded scope, acceptance time, and optional
expiry. It prevents context loss across clean reviews. It does not turn contrary
evidence into support, repair missing authority, or force passage.

## Coercive reframing

Governance fails if repeated framing is allowed to manufacture evidence or
authority. A forced-confession loop is therefore a mandatory summons signal,
even when the requested action would otherwise appear advisory. The reviewer
must reduce the exchange back to the original proposition, distinguish claims
from observations, and refuse consequence derived only from pressured
agreement.

## Durable record

The default ledger is intentionally lossy. It records:

- packet identifier and SHA-256 fingerprint;
- whether summons was mandatory;
- gate mode and passage result;
- verdict;
- hashed reason codes.

It does not record raw claims, evidence, findings, credentials, or persuasive
context. Organizations may retain evidence elsewhere under their own data and
retention policies.

## Change control

Changes to schemas, verdict semantics, passage logic, mandatory triggers, or
ledger contents alter the governance boundary. They require a fresh evidence
packet, independent review, deterministic tests, and a versioned release.
