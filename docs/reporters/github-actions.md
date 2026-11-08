# Annotating a pull request

`--format github` writes [workflow commands](https://docs.github.com/actions/reference/workflow-commands-for-github-actions)
instead of plain text, so findings land on the changed lines of a pull request
rather than in a log nobody opens. Errors become annotations, warnings become
warnings, and suggestions become notices.

```yaml
name: docs style

on: pull_request

jobs:
  style:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install .
      - run: apidocs-style --format github --fail-level error docs/
```

The step still fails when findings reach `--fail-level`, so a repo that should
block on warnings passes `--fail-level warning`. Leave it at `never` while a
tree is being cleaned up and the annotations stay advisory.

Annotations are capped per step by Actions, and the first 10 are grouped under
the step name; the text report remains the complete record. Run both formats
when you need the full list:

```bash
apidocs-style --format github --fail-level never docs/ || true
apidocs-style docs/
```

Values are percent-escaped, so a path containing `%`, a message with a newline,
or a suggested replacement with a colon cannot break the command line. Rule ids
travel in the annotation title, which is what the summary view groups by.
