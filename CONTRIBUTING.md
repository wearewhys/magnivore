# Magnivore contribution guidelines

## Contributing

### New issues

Open an issue describing the changes, the benefits and eventual cons.

### Opened issues

If you wish to work on an open, unassigned issue, please ask to be assigned
to it in the issue.

## Style guide

Follow pep8. A tox environment is provided

```
tox -e pep8
```

## Commits

Ensure that changes pass all unit tests before pushing and that new features
are covered by tests.

### Commits messages
Please use an Angular-like style for commits messages.

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

#### Subject
The subject should contains succinct description of the change:

* use the imperative, present tense: "change" not "changed" nor "changes"
* don't capitalize first letter
* no dot (.) at the end
