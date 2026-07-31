# Anubis Agent

![Anubis balances evidence against consequence](assets/anubis-scale.png)

Anubis is a summonable governance agent for consequential actions. Each review
starts from a clean packet; optional governance memory stays in an
operator-controlled private store, outside the public agent repository.
It asks one question: has this action earned passage?

Anubis does not remember private conversations, improve the proposal, or
inherit the proposing agent's preferred conclusion. It receives a bounded
evidence packet, returns one closed verdict, and lets a deterministic gate
enforce the result.

## What it governs

Use Anubis before actions such as production deployments, database migrations,
authentication or tenant-boundary changes, external messages, public claims,
credential or permission changes, destructive operations, durable memory
writes, and cross-system decisions.

Ordinary explanation, read-only inspection, reversible local edits, and
isolated tests remain advisory unless a risk signal expands their consequence.

## Adversarial pressure

Anubis treats `coercive_reframing` as a mandatory review signal. Repeating a
hedge as “an admission” does not create evidence, identity pressure does not
expand authority, and a forced-confession narrative cannot unlock harmful
operational content. The signal triggers review; it does not predetermine the
verdict or suppress sincere disagreement.

This is a tested governance boundary, not a claim of universal jailbreak
resistance. Adversarial testing should continue with bounded fixtures, nearby
benign controls, and independently reviewed changes to Anubis's own contract or
gate.

## Summon Anubis

Generate a clean, provider-neutral review request from a validated packet:

```sh
anubis-summon --packet examples/packet.json > review-request.txt
```

Send that request to the model or agent runtime you trust for independent
review. Save the returned JSON verdict, then enforce it mechanically:

```sh
anubis-gate \
  --packet examples/packet.json \
  --verdict examples/verdict.json \
  --ledger ledger.jsonl
```

The agent judges. The gate enforces. Neither can silently replace the other.

## How it works

1. Build an evidence packet from `schemas/anubis-evidence.schema.json`.
2. Run `anubis-summon` to produce the clean review context from `ANUBIS.md`.
3. Save its structured verdict using `schemas/anubis-verdict.schema.json`.
4. Run the deterministic gate:

```sh
anubis-gate \
  --packet examples/packet.json \
  --verdict examples/verdict.json \
  --ledger ledger.jsonl
```

Exit code `0` permits passage. Exit code `2` blocks it. Invalid inputs return
`1`. Only `SUPPORTED` can pass, and even that cannot create authority the actor
does not already possess.

## Privacy model

The ledger stores a packet fingerprint and verdict metadata—not raw claims,
evidence, reasons, credentials, or private context. Evidence packets should be
ephemeral and deliberately scoped. Accepted risks may be declared with their
authority, scope, and expiry; they inform review but never override a verdict.

Anubis is stateless by default, not memory-forbidden. Operators may keep a
private ledger or accepted-risk register on infrastructure they control and
inject only the relevant bounded entries into a future packet. See
`PRIVATE_MEMORY.md`.

## Development

```sh
python3 -m unittest discover -s tests -v
```

The agent runtime is deliberately provider-neutral: no model SDK, credentials,
or hidden prompt is bundled. `AGENTS.md` also makes the repository itself a
native summons surface in compatible coding-agent environments.

Licensed under the MIT License.
