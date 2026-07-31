# Optional private governance memory

Anubis reviews are clean-context by default. That does not require an operator
to forget every prior decision.

An operator may keep governance memory in a private system it controls, such as
an encrypted local store, private server, or internal agent memory. The public
Anubis repository neither receives nor hosts that data.

## Suitable records

- packet fingerprints and verdict metadata;
- accepted risks with accepting authority, scope, timestamp, and expiry;
- policy versions and gate versions;
- reproducibility method identifiers;
- public evidence locators and content digests.

## Records that stay out

- credential or token values;
- raw sensitive evidence unless separately required and protected;
- unrelated conversation memory;
- the proposing agent's persuasive reasoning or preferred verdict;
- inferred authority or identity claims.

At summons time, retrieve only the records relevant to the exact claim and
action. Put them into the declared packet fields. Anubis judges the supplied
packet; it does not silently search private memory for reasons to pass or block.

The default JSONL ledger is intentionally lossy and may be stored privately. It
contains fingerprints and verdict metadata, not raw packet content.
