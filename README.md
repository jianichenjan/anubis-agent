# Anubis Agent

![Anubis balances evidence against consequence](assets/anubis-scale-cadentis-counterweight-3d-v1.png)

Anubis is a summonable governance agent for consequential actions. Each review
starts from a clean packet; optional governance memory stays in an
operator-controlled private store, outside the public agent repository.
It asks one question: has this action earned passage?

Anubis does not remember private conversations, improve the proposal, or
inherit the proposing agent's preferred conclusion. It receives a bounded
evidence packet, returns one closed verdict, and lets a deterministic gate
enforce the result.

## Selective by design

Anubis is deliberately not present in every interaction. Constant review would
add theater and latency without improving low-consequence work. The summons
policy is explicit: local explanation and isolated tests can remain advisory;
deployments, migrations, permission changes, tenant-boundary changes, public
claims, external messages, destructive actions, and durable memory cross the
gate in a compliant integration.

Selection inside the library is mechanical. The action, risk signals, blast
radius, external exposure, and reversibility declared in the packet determine
whether review is mandatory. Anubis does not independently discover omitted or
misclassified consequences; a trustworthy integration must construct that
packet from authoritative state and stop the action while review is pending.

## Governance you can inspect

The public repository exposes the parts an operator should be able to verify:

| Published | Deliberately withheld |
|---|---|
| summons triggers and risk signals | credentials and tokens |
| evidence and verdict schemas | raw private evidence |
| closed verdict vocabulary | private conversations and persuasive reasoning |
| deterministic allow/block conditions | hidden authority or silent overrides |
| privacy-preserving ledger format | unrelated operator memory |
| tests for passage and refusal | claims of universal jailbreak resistance |

This is transparency about the decision boundary, not indiscriminate disclosure.
The ledger records a packet fingerprint, verdict metadata, and hashed reason
codes. It does not become a second archive of the material it governs.

## Two independent controls

```text
clean evidence packet → independent judgment → structured verdict
                                             ↓
proposed consequence ← deterministic allow/block gate ← verdict + packet
```

The reviewer contract grants no execution authority. The enforcement gate cannot
invent a better verdict. Only `SUPPORTED` passes when the gate is invoked, and it
still cannot create authority the caller did not already possess.

That separation is the point. Governance should not depend on trusting the same
agent to propose, review, approve, and execute its own action. This library
enforces the packet/verdict boundary; the surrounding system remains responsible
for intercepting the real consequence and honoring the exit result.

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

## What Anubis does not solve

- It does not authenticate the human holding an already authenticated device.
- It does not make weak or stale evidence true.
- It does not establish identity, grant authority, or expand the scope of the
  action under review.
- It does not guarantee that every harmful prompt or trajectory will be detected.
- It does not authorize itself to change its own governing contract or gate.

Those limits are part of the interface. A governance layer becomes less
trustworthy when its failure boundaries are hidden behind stronger language.

## Summon Anubis

Use the fail-closed entry point for integrations. Mandatory packets without a
verdict emit a clean review request and exit `3`; callers must stop the proposed
action, obtain a verdict, then invoke the same command again with `--verdict`:

```sh
python3 -m anubis.entrypoint --packet examples/packet.json > review-request.txt
python3 -m anubis.entrypoint --packet examples/packet.json \
  --verdict examples/verdict.json \
  --ledger ledger.jsonl
```

Exit code `0` permits passage, `2` blocks passage, `3` requires independent
review, and `1` means the packet or verdict is invalid. This is the recommended
single local orchestration surface. A compliant caller treats exit `3` as a hard
stop and does not mistake the emitted summons request for approval.

Generate a clean, provider-neutral review request from a validated packet:

```sh
python3 -m anubis.summon --packet examples/packet.json > review-request.txt
```

Send that request to the model or agent runtime you trust for independent
review. Save the returned JSON verdict, then enforce it mechanically:

```sh
python3 -m anubis.gate \
  --packet examples/packet.json \
  --verdict examples/verdict.json \
  --ledger ledger.jsonl
```

The agent judges. The gate enforces. Neither can silently replace the other.

## Add Anubis to an agent hook

For a Python agent, the integration boundary is one callback: your provider
adapter receives Anubis's review request and returns the structured verdict.
The helper never executes the proposed action; your code calls `enforce` only
after the result has been returned.

```python
from anubis.integration import enforce, review_action

def ask_reviewer(review_request: str) -> dict:
    # Send review_request to your approved model or review service.
    return provider.complete_json(review_request)

result = review_action(packet, ask_reviewer, ledger="var/anubis.jsonl")
enforce(result)
perform_the_action()
```

Mandatory packets stop at the review callback. A blocked or invalid verdict
raises before `perform_the_action()` is reached; advisory packets return an
explicit allowed result for low-consequence work. For non-Python runtimes,
use the CLI entrypoint or mirror the same three-stage contract: propose,
review, then enforce.

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
or hidden prompt is bundled.

Licensed under the MIT License.
