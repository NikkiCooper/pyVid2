---
name: Feature Request
about: Suggest a new feature or enhancement
title: "[Feature] "
labels: enhancement
assignees: ''
---

body:
  - type: markdown
    attributes:
      value: |
        Got an idea? Let me know!

  - type: input
    id: summary
    attributes:
      label: Feature Summary
      placeholder: "Add support for XYZ"

  - type: textarea
    id: motivation
    attributes:
      label: Why is this needed?
      placeholder: "It would help users do ABC more easily"

  - type: textarea
    id: details
    attributes:
      label: Additional Details
      placeholder: "Any mockups, diagrams, or examples?"
