Maka
====
Maka is simple, configurable software for the efficient collection of textual animal behavioral observations. To configure Maka for a particular project you specify:

1. The types and syntax of the *observations* to be collected. There can be any number of different types of observations.

2. The syntax of *commands* that will be typed to create observations, and how observations will be created from them. The commands are typically more terse than the observations, so that data can be collected efficiently.

You collect data with Maka by typing commands that are expanded into observations that are added to the current *document*. A document is a list of observations, displayed as text with one observation per line. The observations of a document can be edited individually, or groups of them can be cut, copied, and pasted. Whenever you edit an observation, Maka ensures that your modifications conform to the defined observation syntax, protecting the integrity of your data and simplifying subsequent data processing.

## Requirements

- Python 3.6 or later
- PySide6 (Qt 6 bindings for Python)
- pyserial (for theodolite serial communication support)

## Installation

1. Install Python 3.6 or later if not already installed.

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run Maka:
   ```bash
   PYTHONPATH=src python3 src/maka/Maka.py
   ```

## Running Tests

To run the test suite:
```bash
PYTHONPATH=src python3 -m unittest discover -s test -p "*Tests.py"
```

For more detailed information, see the [installation instructions](https://github.com/HaroldMills/Maka/wiki/Installation).
