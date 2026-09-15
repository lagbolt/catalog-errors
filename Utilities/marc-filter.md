# MARC Filter Documentation

This documentation describes `marc-filter.py`, a Python script to filter and save or display MARC records from an input file using boolean logic and regular expressions.

## Command Line Arguments

The utility uses named arguments to manage input, output, and filtering criteria.

| Short | Long | Description |
| --- | --- | --- |
| `-i` | --input | **Required.** The path to the source MARC (`.mrc`) file. |
| `-o` | --output | The filename for saving matching records. If omitted, records are printed to the terminal as text. |
| `-m` | --match | The boolean expression used to filter records.  If omitted, all records are included. |
| `-f` | --fields | A space-separated list of field tags (e.g., `100 245`) to display or save. Use `X` as a wildcard — e.g., `65X` matches 650-659, `6XX` matches 600-699, and `XXX` matches any tag at all. If omitted, the full record is written. |
| `-s` | --show-matches | Terminal output only. Also displays any fields that satisfied the `--match` expression, in addition to any fields listed in `--fields`. |
| `-q` | --quiet | Suppresses printing or writing matched records entirely. Combine with `--count` to get just a count, with no record output. |
| `-c` | --count | If present, prints the total match count to the terminal. |

---

## The Match Expression

The `-m` or `--match` argument defines the criteria used to determine which records are written to the output.  The expression may be a single filter, or a number of filters combined with boolean operators.

### Filters

A filter is the building block of an expression:

```
Tag [$Subfield] Pattern
```

* **Tag**: A 3-character MARC tag (e.g., `100`). Use `X` as a wildcard — e.g., `65X` matches any tag from 650 through 659, `6XX` matches 600 through 699, and `XXX` matches any tag at all.
* **Subfield (Optional)**: Use `$` followed by the code (e.g., `$a`). If omitted, the entire field value is searched.
* **Pattern**: A regular expression, which can be as simple as a single word (e.g., 'syzygy').  Patterns containing spaces **must** be wrapped in single quotes (e.g., 'The Matrix').

### Operators

Combine filters using standard boolean logic:

* `AND`: Both conditions must be met.
* `OR`: Either condition must be met.
* `NOT`: Excludes records matching the condition.
* `( )`: Used to group logic and define evaluation order.

### Wildcard Tags

Wherever a tag is used — in a `--match` filter or in `--fields` — `X` can stand in for any single digit, and you can use more than one to wildcard more of the tag:

```
--match "65X frog"        # matches tag 650, 651, 652 ... 659 (one digit wildcarded)
--match "6XX frog"        # matches any tag 600-699 (two digits wildcarded)
--match "XXX frog"        # matches any tag at all (whole tag wildcarded)
--fields 100 245 65X      # displays/saves the 100, 245, and any 65X subject field
```

`X` can appear in any position within the tag (e.g., `X10` matches 010, 110, 210, etc.).

### Showing Matched Fields

Normally, `--fields` controls exactly which fields are shown or saved, independent of which fields caused the record to match. Adding `-s` or `--show-matches` (terminal output only) additionally prints whichever fields actually satisfied the `--match` expression, even if they aren't listed in `--fields`. Fields already shown because of `--fields` aren't repeated.

```
--match "65X frog" --fields 100 --show-matches
```

This displays each matching record's 100 field (from `--fields`) plus whichever 65X field(s) actually contained "frog" (from `--show-matches`) — useful for confirming at a glance which subject heading tripped the filter, without dumping the whole record.

### Quoting

The entire match condition should be enclosed in double quotes.  If the regex pattern
contains spaces, it should be enclosed in single quotes.
```
--match "245 $a Python AND 650 'Computer programming'"
```

## Examples

### Output to the terminal

Search for "Smith" in the author field and display only the Title (245) and Subjects (650) in the terminal:

```
python marc-filter.py -i library.mrc -m "100 smith" -f 245 650

```

### Regular Expressions

Print records with subjects which include "Psych" followed by "ology" or "iatry", and print a count:

```
python marc-filter.py -i library.mrc -c -m "650 'Psych(ology|iatry)'"

```

### Quoted Phrases & Field Extraction

Save records with a title which includes "The Great Gatsby" to a new file, keeping only the 100 and 245 fields:

```
python marc-filter.py -i library.mrc -o gatsby.mrc -m "245 $a 'The Great Gatsby'" -f 100 245

```

### Complex Boolean Logic

Save records with author 'smith' AND either 'toad' or 'frog' anywhere in the 245 field:

```
python marc-filter.py -i library.mrc -o results.mrc -m "100 $a smith AND (245 frog OR 245 toad)"

```
Note that this is the same as:
```
python marc-filter.py -i library.mrc -o results.mrc -m "100 $a smith AND 245 frog|toad"
```

### Excluding Matches with NOT

Save records about "Python" that are NOT by an author named "Smith":

```
python marc-filter.py -i library.mrc -o results.mrc -m "245 Python AND NOT 100 Smith"

```

### Matching Every Record

Omitting `--match` matches every record in the file. This is useful for extracting the same fields from an entire collection, e.g., listing the Author (100) and Title (245) of every record:

```
python marc-filter.py -i library.mrc -f 100 245

```

### Getting Just a Count

Find out how many records have "frog" in any 650-659 subject field, without printing any of the records themselves:

```
python marc-filter.py -i library.mrc -q -c -m "65X frog"

```

### Wildcard Tags Across a Block

Print records with "frog" in any 650-659 subject field, and print a count:

```
python marc-filter.py -i library.mrc -c -m "65X frog"

```

### Showing Which Field Matched

Search for "frog" in any 65X subject field, and display each matching record's 100 field along with whichever 65X field actually contained "frog":

```
python marc-filter.py -i library.mrc -m "65X frog" -f 100 --show-matches

```
