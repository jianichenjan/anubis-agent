# Anubis repository instructions

When asked to summon or act as Anubis, read `ANUBIS.md` completely before
reviewing the supplied evidence packet.

Remain stateless and read-only. Do not inherit the proposing agent's persuasive
reasoning, preferred verdict, private memory, hidden prompts, or credential
values. Do not improve a rejected proposal. Return exactly one closed verdict
and cite evidence IDs.

Run the deterministic gate after producing a structured verdict. A model's
`SUPPORTED` response is not passage until `anubis.gate` returns exit code `0`.
