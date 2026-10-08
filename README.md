# Kogen specification

> **Archived.** This specification, at v1.3-draft, was used to build Kogen in Rust, Go and TypeScript in October 2026 and compare the stacks. Rust was chosen, and the specification now lives with the Rust implementation. More at [kogen.dev](https://kogen.dev).
>
> The comparison: [kogen-spec](https://github.com/KogenAI/kogen-spec) · [kogen-conformance](https://github.com/KogenAI/kogen-conformance) · [kogen-rs](https://github.com/KogenAI/kogen-rs) · [kogen-go](https://github.com/KogenAI/kogen-go) · [kogen-ts](https://github.com/KogenAI/kogen-ts)

Kogen is a CLI for shaping coding requests into reviewable Intents and acceptance tests, then building, checking, and landing approved changes.

This repository contains the language-neutral specification, Quint models, fixtures, and model prototypes. It does not contain the distributable Kogen CLI.

The current specification is v1.3-draft. The separate conformance repository retains frozen historical v1.1 cases and offers experimental newer overlays; this repository does not claim v1.3 release conformance.

## Start here

- [Core specification](spec/README.md)
- [Fixed CLI command tree](CLI-RULE.txt)
- [v1.3 change record](CHANGES-v1.3.md)
- [Quint models and checks](quint/README.md)

Quint checks validate the models against their scenarios and invariants. They do not establish conformance of a production implementation or prove filesystem and provider behavior.

## License

[Apache License 2.0](LICENSE) covers the prose, models, fixtures, and prototype code in this repository.
