---
name: Bug Report / Feature Request
description: Report a bug or request a new feature
title: "[BUG] "  # or "[FEATURE] "
labels: []
assignees: ''

body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to improve the Smart Route Optimizer! 
        Please fill out the template below to help us investigate.

  - type: dropdown
    id: issue-type
    attributes:
      label: Issue Type
      description: Are you reporting a bug or requesting a feature?
      options:
        - Bug Report
        - Feature Request
        - Question / Support
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Clear description of the bug or feature
      placeholder: |
        **Bug:** What happened? What did you expect?
        **Feature:** What should it do? Why is it useful?
    validations:
      required: true

  - type: textarea
    id: steps-to-reproduce
    attributes:
      label: Steps to Reproduce (for bugs)
      placeholder: |
        1. Start server with '...'
        2. Call endpoint '/optimize' with '...'
        3. See error

  - type: textarea
    id: environment
    attributes:
      label: Environment
      description: OS, Python version, package versions
      value: |
        - OS: [e.g. Ubuntu 22.04, macOS 13]
        - Python: [e.g. 3.10.12]
        - Package versions: [output of `pip freeze`]
    validations:
      required: false

  - type: textarea
    id: logs
    attributes:
      label: Relevant Log Output
      description: Paste any error messages or stack traces
      render: shell

  - type: checkboxes
    id: checks
    attributes:
      label: Confirmations
      description: Please check all that apply
      options:
        - label: I have searched existing issues (both open & closed)
        - label: I have included a complete, minimal code example when applicable
        - label: I have attached relevant logs/screenshots

  - type: textarea
    id: additional-context
    attributes:
      label: Additional Context
      description: Any other information, screenshots, mock data, etc.
