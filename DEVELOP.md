# Development

This page describes how to set up a development environment for the project.


## Setting up

Install the poetry dotenv plugin:

```
poetry self add poetry-dotenv-plugin
```


## Running the project

To run the project, use the following command:

```
poetry run python -m llm4data
```

## Checklists before committing

- [ ] Run `make format` to format the code
- [ ] Run `make lint` to lint the code
- [ ] Sign-off commits with `git commit -s`


## Publishing to PyPI

To publish to PyPI, use the following command:

```
poetry publish --build
```

## Publishing to TestPyPI

To publish to TestPyPI, use the following command:

```
poetry publish --build --repository testpypi
```

## Publishing to GitHub Packages

To publish to GitHub Packages, use the following command:

```
poetry publish --build --repository gh-package
```
