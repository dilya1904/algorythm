"""
Unit and Integration Tests for Boyer-Moore Search Algorithms & FastAPI Endpoints
"""

import unittest
from algorithms import (
    build_bad_character_table,
    compute_good_suffix_shift,
    run_boyer_moore_bad_char,
    run_boyer_moore_good_suffix,
    compare_boyer_moore,
)
from main import (
    read_root,
    health_check,
    get_presets,
    search,
    search_sample,
    SearchRequest,
)


class TestBoyerMooreAlgorithms(unittest.TestCase):
    def test_bad_character_table(self):
        # G(0), C(1), G(2), T(3), A(4), G(5)
        table = build_bad_character_table("GCGTAG")
        self.assertEqual(table["G"], 5)  # last G at index 5
        self.assertEqual(table["C"], 1)
        self.assertEqual(table["T"], 3)
        self.assertEqual(table["A"], 4)

    def test_good_suffix_shift(self):
        shift = compute_good_suffix_shift("GCGTAG", 4)
        self.assertGreaterEqual(shift, 1)

    def test_run_bad_character_matches(self):
        text = "GCATGCGTAGGTAGCGTAGAG"
        pattern = "GCGTAG"
        result = run_boyer_moore_bad_char(text, pattern)
        self.assertIn(4, result["matches"])
        self.assertIn(13, result["matches"])
        self.assertEqual(len(result["matches"]), 2)
        self.assertGreater(len(result["history"]), 0)
        self.assertIn("time_complexity", result["history"][0])
        self.assertIn("array", result["history"][0])

    def test_run_good_suffix_matches(self):
        text = "GCATGCGTAGGTAGCGTAGAG"
        pattern = "GCGTAG"
        result = run_boyer_moore_good_suffix(text, pattern)
        self.assertIn(4, result["matches"])
        self.assertIn(13, result["matches"])
        self.assertEqual(len(result["matches"]), 2)
        self.assertGreater(len(result["history"]), 0)

    def test_compare_boyer_moore(self):
        result = compare_boyer_moore("GCATGCGTAGGTAGCGTAGAG", "GCGTAG")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["benchmark"]["matches_count"], 2)
        self.assertIn("bc_comparisons", result["benchmark"])
        self.assertIn("gs_comparisons", result["benchmark"])
        self.assertIn("efficiency_gain_pct", result["benchmark"])


class TestFastAPIEndpoints(unittest.TestCase):
    def test_root_endpoint(self):
        res = read_root()
        self.assertEqual(res["status"], "online")
        self.assertIn("endpoints", res)

    def test_health_endpoint(self):
        res = health_check()
        self.assertEqual(res["status"], "healthy")

    def test_search_endpoint(self):
        req = SearchRequest(text="GCATGCGTAGGTAGCGTAGAG", pattern="GCGTAG")
        res = search(req)
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["benchmark"]["matches_found"]), 2)
        self.assertIn("bad_character", res)
        self.assertIn("good_suffix", res)

    def test_search_presets(self):
        presets = get_presets()
        self.assertGreaterEqual(len(presets), 3)

    def test_search_sample(self):
        res = search_sample()
        self.assertEqual(res["status"], "success")


if __name__ == "__main__":
    unittest.main()
