# vale-api-guide

A style guide for API reference pages, shipped twice over: as [Vale](https://vale.sh)
rules for editors and CI, and as a fast local checker for the parts of review
that should never reach a human.

Both surfaces carry the same rule ids, so a page that fails locally fails CI
for the readable reason, and both agree about what "good" means. The guide
targets reference pages: request and response sections, parameter tables,
error catalogues. Prose tutorials are welcome to be chattier.

## Prerequisites

- Python 3.10 or newer for the local checker
- [Vale](https://vale.sh/docs/install) 3.x if you want the same rules in your editor or CI
- A page tree you own; this tool does not generate or rewrite docs

## Install

```bash
git clone https://github.com/ftlw9bqfhq/vale-api-guide.git
cd vale-api-guide
pipx install .
```

For the Vale half, point your config at the bundled styles and copy them into
`StylesPath`:

```bash
mkdir -p "$HOME/.config/vale/styles"
cp -r styles/APIReference "$HOME/.config/vale/styles/"
```

Then reuse the supplied config, which raises the fence-language rule to an
error and keeps prose rules as warnings:

```bash
cp .vale.ini /path/to/your/docs/.vale.ini
```

Rule ids are stable. If you silence one in a `vale.ini` override or a
`<!-- vale off -->` block, note why in the PR.

## Usage

Check a directory and fail the run on warnings or worse:

```bash
apidocs-style docs/
```

The same run through the source tree, without installing:

```bash
python -m apidocs_style.cli docs/
```

Report only errors, or emit JSON for another tool:

```bash
apidocs-style --min-level error docs/
apidocs-style --format json docs/ > report.json
```

Advisory-only pass that always exits 0:

```bash
apidocs-style --fail-level never docs/
```

Output on the bundled example page:

```console
$ apidocs-style examples/
examples/list-charges.md:17:1: error APIRef.CodeFenceLanguage Fenced code block has no language tag.
    Tag the fence, for example ```json, so readers and highlighters can parse it.
    > ```
examples/list-charges.md:24:58: warning APIRef.FutureTense Future tense for behavior that happens now.
    Use the present tense: 'the server returns'.
    > A charge object is returned for each entry. The `amount` will be returned in the smallest currency unit.
examples/list-charges.md:26:1: warning APIRef.WordyPhrase Wordy phrase.
    Use 'to', 'before', 'now', 'if', or 'use'.
    > In order to page through results, pass the `starting_after` parameter ...
examples/list-charges.md:3:62: suggestion APIRef.PassiveVoice Passive voice in reference text.
    Name the actor: 'the server returns', not 'is returned'.
    > Returns a paginated list of charges for the account. Charges are returned newest first.

1 file checked: 1 error, 4 warning, 3 suggestion
```

Exit codes: `0` clean, `1` findings at or above `--fail-level`, `2` unreadable path.

## Rules

| Id | Level | Catches |
| --- | --- | --- |
| `APIRef.CodeFenceLanguage` | error | A fence with no language tag |
| `APIRef.CodeFenceClosed` | error | A fence that never closes |
| `APIRef.WordyPhrase` | warning | `in order to`, `prior to`, `utilize` |
| `APIRef.FutureTense` | warning | `will be returned` for current behavior |
| `APIRef.LatinAbbreviation` | warning | `e.g.`, `i.e.`, `etc.` in running prose |
| `APIRef.PassiveVoice` | suggestion | Agentless sentences |
| `APIRef.SecondPerson` | suggestion | `users can` instead of `you can` |
| `APIRef.SentenceLength` | suggestion | Sentences over 25 words |
| `APIRef.TrailingSpace` | suggestion | Whitespace at end of line |

The checker reads fenced code as opaque, ignores inline code and link targets,
and skips YAML front matter, so it stays quiet where prose rules do not apply.
Sentence length and unclosed-fence checks are computed, so they run here and
have no Vale counterpart.

## Layout

```
apidocs_style/       checker: rule catalogue, scanner, CLI
styles/APIReference/ Vale rules, one file per rule id
examples/            a sample page that trips several rules
tests/               scanner regressions
.vale.ini            Vale config for a docs tree
```

## Contributing

Add a rule in `rules.py` and the matching YAML in `styles/APIReference/`, plus
a scanner test that shows the false-positive case it must not flag. Keep new
rules at `warning` unless a build genuinely cannot ship with them: `error`
means "block the merge".

## License

MIT, see [LICENSE](LICENSE).
