# detectors/type4/educational/problem_bank/test_cases.py
"""
Curated test-case banks for each problem category.

Each bank is a list of (input_str, expected_output_str) tuples.

Design principles:
  - inputs  are fed to the harness via stdin (one test per subprocess run)
  - expected outputs are the canonical correct answers
  - I/O comparison uses NORMALIZED outputs (numbers extracted, whitespace
    stripped, case-folded) so that cosmetic differences in student output
    text do not cause false negatives
  - Test cases cover: normal case, edge cases, negatives, duplicates,
    boundary sizes, and adversarial orderings
"""

from typing import List, Tuple

TestCase = Tuple[str, str]   # (stdin_input, expected_stdout_output)


# ─────────────────────────────────────────────────────────────────────────────
# SORT_ARRAY
#   Input:  space-separated integers on one line
#   Output: space-separated sorted integers on one line
# ─────────────────────────────────────────────────────────────────────────────

SORT_ARRAY: List[TestCase] = [
    ("5 3 1 4 2",                    "1 2 3 4 5"),
    ("1",                            "1"),
    ("2 1",                          "1 2"),
    ("1 2 3 4 5",                    "1 2 3 4 5"),          # already sorted
    ("5 4 3 2 1",                    "1 2 3 4 5"),          # reverse sorted
    ("2 2 2 2",                      "2 2 2 2"),            # all duplicates
    ("-3 -1 -5 -2 -4",              "-5 -4 -3 -2 -1"),     # all negatives
    ("64 34 25 12 22 11 90",        "11 12 22 25 34 64 90"), # exam example
    ("100 1",                        "1 100"),
    ("7 6 5 4 3 2 1",               "1 2 3 4 5 6 7"),
    ("10 9 8 7 6 5 4 3 2 1",        "1 2 3 4 5 6 7 8 9 10"),
    ("3 3 1 2 1",                    "1 1 2 3 3"),          # duplicates mixed
    ("0 0 0",                        "0 0 0"),
    ("-1 0 1",                       "-1 0 1"),
    ("100 50 25 75",                 "25 50 75 100"),
    ("8 3 8 1 3",                    "1 3 3 8 8"),
    ("42 42",                        "42 42"),
    ("1000 500 250 125",             "125 250 500 1000"),
    ("-10 10 -10 10",               "-10 -10 10 10"),
    ("9 1 5 3 7 2 8 4 6",           "1 2 3 4 5 6 7 8 9"),
]


# ─────────────────────────────────────────────────────────────────────────────
# STACK_OPERATIONS
#   Input:  sequence of operations, one per line:
#             PUSH <n>  → push integer n
#             POP       → pop and print top
#             PEEK      → print top without removing
#             SIZE      → print current size
#             ISEMPTY   → print 1 if empty, 0 otherwise
#   Output: one result per operation on its own line
#           PUSH → "OK"
#           POP  → integer value (only called when stack has elements)
#           PEEK → integer value (only called when stack has elements)
#           SIZE → integer
#           ISEMPTY → 0 or 1
#
#   Test cases intentionally avoid overflow/underflow to keep expected
#   outputs independent of each student's error-message wording.
# ─────────────────────────────────────────────────────────────────────────────

STACK_OPERATIONS: List[TestCase] = [
    # basic push-peek-pop
    ("PUSH 10\nPEEK\nPOP\nISEMPTY",          "OK\n10\n10\n1"),
    # multiple pushes then size
    ("PUSH 10\nPUSH 20\nPUSH 30\nSIZE",      "OK\nOK\nOK\n3"),
    # LIFO order check
    ("PUSH 1\nPUSH 2\nPUSH 3\nPOP\nPOP\nPOP","OK\nOK\nOK\n3\n2\n1"),
    # isEmpty on fresh stack
    ("ISEMPTY",                               "1"),
    # push then isEmpty
    ("PUSH 5\nISEMPTY",                       "OK\n0"),
    # push pop push peek
    ("PUSH 7\nPOP\nPUSH 9\nPEEK",            "OK\n7\nOK\n9"),
    # size tracking
    ("PUSH 1\nSIZE\nPUSH 2\nSIZE\nPOP\nSIZE","OK\n1\nOK\n2\n2\n1"),
    # LIFO with 4 elements
    ("PUSH 10\nPUSH 20\nPUSH 30\nPUSH 40\nPOP\nPEEK",
     "OK\nOK\nOK\nOK\n40\n30"),
    # interleaved push/pop
    ("PUSH 5\nPUSH 3\nPOP\nPUSH 8\nPEEK\nSIZE",
     "OK\nOK\n3\nOK\n8\n2"),
    # push negative value
    ("PUSH -5\nPEEK\nPOP",                   "OK\n-5\n-5"),
    # push 0
    ("PUSH 0\nPEEK\nISEMPTY",               "OK\n0\n0"),
    # large sequence
    ("PUSH 1\nPUSH 2\nPUSH 3\nPUSH 4\nPUSH 5\nSIZE\nPOP\nPOP\nSIZE",
     "OK\nOK\nOK\nOK\nOK\n5\n5\n4\n3"),
]


# ─────────────────────────────────────────────────────────────────────────────
# LINKED_LIST_OPERATIONS
#   Input:  sequence of operations:
#             INSERT_END <n>    → append n to end
#             INSERT_FRONT <n>  → prepend n
#             DELETE <n>        → delete first occurrence of n
#             SEARCH <n>        → 1 if n exists, 0 otherwise
#             LENGTH            → print list length
#             PRINT             → print space-separated values front-to-back
#   Output: one result per operation on its own line
#           INSERT_END/INSERT_FRONT/DELETE → "OK"
#           SEARCH  → 0 or 1
#           LENGTH  → integer
#           PRINT   → space-separated integers
# ─────────────────────────────────────────────────────────────────────────────

LINKED_LIST_OPERATIONS: List[TestCase] = [
    # basic insert and print
    ("INSERT_END 10\nINSERT_END 20\nINSERT_END 30\nPRINT",
     "OK\nOK\nOK\n10 20 30"),
    # insert front
    ("INSERT_END 20\nINSERT_FRONT 10\nPRINT",
     "OK\nOK\n10 20"),
    # length
    ("INSERT_END 1\nINSERT_END 2\nINSERT_END 3\nLENGTH",
     "OK\nOK\nOK\n3"),
    # delete middle
    ("INSERT_END 10\nINSERT_END 20\nINSERT_END 30\nDELETE 20\nPRINT",
     "OK\nOK\nOK\nOK\n10 30"),
    # delete head
    ("INSERT_END 10\nINSERT_END 20\nDELETE 10\nPRINT",
     "OK\nOK\nOK\n20"),
    # delete tail
    ("INSERT_END 10\nINSERT_END 20\nDELETE 20\nPRINT",
     "OK\nOK\nOK\n10"),
    # search found
    ("INSERT_END 5\nINSERT_END 10\nSEARCH 10",
     "OK\nOK\n1"),
    # search not found
    ("INSERT_END 5\nINSERT_END 10\nSEARCH 99",
     "OK\nOK\n0"),
    # insert front multiple
    ("INSERT_FRONT 3\nINSERT_FRONT 2\nINSERT_FRONT 1\nPRINT",
     "OK\nOK\nOK\n1 2 3"),
    # length after delete
    ("INSERT_END 1\nINSERT_END 2\nINSERT_END 3\nDELETE 2\nLENGTH",
     "OK\nOK\nOK\nOK\n2"),
    # exact replication of student2↔student3 scenario
    ("INSERT_END 10\nINSERT_END 20\nINSERT_END 30\nINSERT_FRONT 5\n"
     "LENGTH\nSEARCH 20\nDELETE 20\nPRINT",
     "OK\nOK\nOK\nOK\n4\n1\nOK\n5 10 30"),
]


# ─────────────────────────────────────────────────────────────────────────────
# LINEAR_SEARCH
#   Input:  line 1 = space-separated array
#           line 2 = target integer
#   Output: 0-based index of target, or -1 if not found
# ─────────────────────────────────────────────────────────────────────────────

LINEAR_SEARCH: List[TestCase] = [
    ("5 3 1 4 2\n3",   "1"),
    ("5 3 1 4 2\n9",   "-1"),
    ("1\n1",           "0"),
    ("1 2 3 4 5\n5",   "4"),
    ("1 2 3 4 5\n1",   "0"),
    ("7 7 7 7\n7",     "0"),    # first occurrence
    ("10 20 30\n20",   "1"),
    ("-3 -1 -5\n-1",   "1"),
    ("100\n100",       "0"),
    ("100\n99",        "-1"),
]


# ─────────────────────────────────────────────────────────────────────────────
# BINARY_SEARCH  (input array is always sorted)
#   Input:  line 1 = sorted space-separated array
#           line 2 = target integer
#   Output: 0-based index of target, or -1 if not found
# ─────────────────────────────────────────────────────────────────────────────

BINARY_SEARCH: List[TestCase] = [
    ("1 3 5 7 9\n5",    "2"),
    ("1 3 5 7 9\n1",    "0"),
    ("1 3 5 7 9\n9",    "4"),
    ("1 3 5 7 9\n6",    "-1"),
    ("1\n1",            "0"),
    ("1\n2",            "-1"),
    ("2 4 6 8 10\n8",   "3"),
    ("1 2 3 4 5\n3",    "2"),
    ("-5 -3 -1 0 2\n-3","1"),
    ("10 20 30 40 50\n10","0"),
]


# ─────────────────────────────────────────────────────────────────────────────
# FIBONACCI
#   Input:  single non-negative integer n
#   Output: F(n) where F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)
# ─────────────────────────────────────────────────────────────────────────────

FIBONACCI: List[TestCase] = [
    ("0",  "0"),
    ("1",  "1"),
    ("2",  "1"),
    ("3",  "2"),
    ("4",  "3"),
    ("5",  "5"),
    ("6",  "8"),
    ("7",  "13"),
    ("8",  "21"),
    ("9",  "34"),
    ("10", "55"),
    ("12", "144"),
    ("15", "610"),
]


# ─────────────────────────────────────────────────────────────────────────────
# FACTORIAL
#   Input:  single non-negative integer n (0 <= n <= 12)
#   Output: n!
# ─────────────────────────────────────────────────────────────────────────────

FACTORIAL: List[TestCase] = [
    ("0",  "1"),
    ("1",  "1"),
    ("2",  "2"),
    ("3",  "6"),
    ("4",  "24"),
    ("5",  "120"),
    ("6",  "720"),
    ("7",  "5040"),
    ("10", "3628800"),
    ("12", "479001600"),
]


# ─────────────────────────────────────────────────────────────────────────────
# GCD  (Greatest Common Divisor)
#   Input:  two positive integers on one line
#   Output: GCD(a, b)
# ─────────────────────────────────────────────────────────────────────────────

GCD: List[TestCase] = [
    ("12 8",    "4"),
    ("100 75",  "25"),
    ("17 5",    "1"),
    ("0 5",     "5"),
    ("5 0",     "5"),
    ("1 1",     "1"),
    ("48 36",   "12"),
    ("7 7",     "7"),
    ("100 1",   "1"),
    ("1000 500","500"),
    ("56 98",   "14"),
    ("270 192", "6"),
]


# ─────────────────────────────────────────────────────────────────────────────
# IS_PALINDROME
#   Input:  a string (may contain spaces, lowercase only)
#   Output: 1 if palindrome, 0 otherwise
# ─────────────────────────────────────────────────────────────────────────────

IS_PALINDROME: List[TestCase] = [
    ("racecar",    "1"),
    ("hello",      "0"),
    ("level",      "1"),
    ("a",          "1"),
    ("ab",         "0"),
    ("abba",       "1"),
    ("abcba",      "1"),
    ("abcde",      "0"),
    ("noon",       "1"),
    ("madam",      "1"),
    ("openai",     "0"),
    ("kayak",      "1"),
]


# ─────────────────────────────────────────────────────────────────────────────
# STRING_REVERSE
#   Input:  a string (no spaces)
#   Output: reversed string
# ─────────────────────────────────────────────────────────────────────────────

STRING_REVERSE: List[TestCase] = [
    ("hello",    "olleh"),
    ("abc",      "cba"),
    ("a",        "a"),
    ("abba",     "abba"),
    ("12345",    "54321"),
    ("python",   "nohtyp"),
    ("racecar",  "racecar"),
    ("xyz",      "zyx"),
    ("code",     "edoc"),
    ("abcde",    "edcba"),
]
