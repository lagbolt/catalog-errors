# MARC Filter Documentation

This documentation describes `marc-filter.py`, a Python script to filter and save or display MARC records from an input file using boolean logic and regular expressions.

## Command Line Arguments

The utility uses named arguments to manage input, output, and filtering criteria.

| Short | Long | Description |
| --- | --- | --- |
| `-i` | --input | **Required.** The path to the source MARC (`.mrc`) file. |
| `-o` | --output | The filename for saving matching records. If omitted, records are printed to the terminal as text. |
| `-m` | --match | The boolean expression used to filter records.  If omitted, all records are included. |
| `-f` | --fields | A space-separated list of field tags (e.g., `100 245`) to display or save. If omitted, the full record is written. |
| `-c` | --count | If present, prints the total match count to the terminal. |

---

## The Match Expression

The `-m` or `--match` argument defines the criteria used to determine which records are written to the output.  The expression may be a single filter, or a number of filters combined with boolean operators.

### Filters

A filter is the building block of an expression:

```
Tag [$Subfield] Pattern
```

* **Tag**: A 3-digit MARC tag (e.g., `100`).
* **Subfield (Optional)**: Use `$` followed by the code (e.g., `$a`). If omitted, the entire field value is searched.
* **Pattern**: A regular expression, which can be as simple as a single word (e.g., 'syzygy').  Patterns containing spaces **must** be wrapped in single quotes (e.g., 'The Matrix').

### Operators

Combine filters using standard boolean logic:

* `AND`: Both conditions must be met.
* `OR`: Either condition must be met.
* `NOT`: Excludes records matching the condition.
* `( )`: Used to group logic and define evaluation order.

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
python marcfilter.py -i library.mrc -m "100 smith" -f 245 650

```

### Regular Expressions

Find records with subjects which include "Psych" followed by "ology" or "iatry":

```
python marcfilter.py -i library.mrc -c -m "650 'Psych(ology|iatry)'"

```

### Quoted Phrases & Field Extraction

Save records with a title which includes "The Great Gatsby" to a new file, keeping only the 100 and 245 fields:

```
python marcfilter.py -i library.mrc -o gatsby.mrc -m "245 $a 'The Great Gatsby'" -f 100 245

```

### Complex Boolean Logic

Save records with author 'smith' AND either 'toad' or 'frog' anywhere in the 245 field:

```
python marcfilter.py -i library.mrc -o results.mrc -m "100 $a smith AND (245 frog OR 245 toad)"

```
Note that this is the same as:
```
python marcfilter.py -i library.mrc -o results.mrc -m "100 $a smith AND 245 frog|toad"
```
