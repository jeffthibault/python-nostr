# Testing python-nostr

## Set up the test environment

Install the test-runner dependencies:
```
pip3 install -r test/requirements.txt
```

Then make the `nostr` python module visible/importable to the tests by installing the local dev dir as an editable module:
```
# from the repo root
pip3 install -e .
```

## Running the test suite
Run the whole test suite:
```
# from the repo root
pytest
```

Run a specific test file:
```
pytest test/test_this_file.py
```

Run a specific test:
```
pytest test/test_this_file.py::test_this_specific_test
```