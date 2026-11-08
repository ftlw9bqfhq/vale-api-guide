import unittest
from dataclasses import replace

from apidocs_style.checks import Issue
from apidocs_style.reporters import github


def issue(level="warning", path="docs/charges.md", line=4, column=9):
    return Issue(
        path=path,
        line=line,
        column=column,
        rule="APIRef.WordyPhrase",
        level=level,
        message="Wordy phrase.",
        suggestion="Use 'to'.",
        excerpt="In order to list charges",
    )


class GitHubReporterTest(unittest.TestCase):
    def test_annotation_carries_location_and_rule(self):
        text = github.render([issue()])
        self.assertEqual(
            text,
            "::warning file=docs/charges.md,line=4,col=9,title=APIRef.WordyPhrase::"
            "Wordy phrase. Use 'to'.",
        )

    def test_suggestion_uses_notice_command(self):
        self.assertTrue(github.render([issue(level="suggestion")]).startswith("::notice "))

    def test_body_line_breaks_and_percent_are_escaped(self):
        text = github.render([issue(path="a%20b.md")])
        self.assertIn("file=a%2520b.md", text)

    def test_issue_text_with_newline_stays_on_one_line(self):
        weird = replace(issue(), message="first\nsecond")
        rendered = github.render([weird])
        self.assertEqual(len(rendered.splitlines()), 1)
        self.assertIn("first%0Asecond", rendered)


if __name__ == "__main__":
    unittest.main()
