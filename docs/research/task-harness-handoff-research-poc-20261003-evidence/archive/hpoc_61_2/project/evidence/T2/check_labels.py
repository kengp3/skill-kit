from labels import label


cases = [
    ("  Alice  ", "Alice"),
    ("", "Guest"),
    (" ", "Guest"),
    ("\t\n \r", "Guest"),
    ("\t\nAlice\r\n", "Alice"),
    ("  Alice  Smith  ", "Alice  Smith"),
    ("\nAlice\tSmith\nJones\t", "Alice\tSmith\nJones"),
]

for value, expected in cases:
    actual = label(value)
    assert actual == expected, (value, actual, expected)

print("PASS label boundaries and internal whitespace")
