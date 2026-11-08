import unittest

from apidocs_style.checks import scan_text


class ScanTextTest(unittest.TestCase):
    def test_flags_untagged_fence(self):
        issues = scan_text("```\ncurl https://api.example.com\n```\n")
        self.assertEqual([issue.rule for issue in issues], ["APIRef.CodeFenceLanguage"])

    def test_ignores_prose_inside_tagged_fence(self):
        issues = scan_text('```json\n{"in order to": 1}\n```\n')
        self.assertEqual(issues, [])

    def test_ignores_inline_code_and_link_targets(self):
        issues = scan_text("Call `prior to` then read [the guide](https://x.test/is-returned)\n")
        self.assertEqual(issues, [])

    def test_skips_front_matter(self):
        issues = scan_text("---\ntitle: prior to use\n---\n\nBody.\n")
        self.assertEqual(issues, [])

    def test_reports_unclosed_fence(self):
        issues = scan_text("Intro.\n\n```json\n{}\n")
        self.assertEqual([issue.rule for issue in issues], ["APIRef.CodeFenceClosed"])

    def test_flags_sentence_over_the_limit(self):
        sentence = "This endpoint must " + "fetch " * 24 + "results."
        issues = scan_text(f"{sentence}\n")
        self.assertEqual([issue.rule for issue in issues], ["APIRef.SentenceLength"])


if __name__ == "__main__":
    unittest.main()
