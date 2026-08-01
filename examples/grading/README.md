# Example grading

This folder shows the smallest post-action feedback loop:

```text
review result → action outcome → explicit assessment
```

The example is synthetic. It contains no project data, conversation text, or
credentials. `review-result.json` is the bounded result returned by Anubis.
`grade.json` records an operator's explicit assessment after the action.

Create a grade in Python:

```python
from pathlib import Path

from anubis.grading import append_grade, grade_result

result = load_json("examples/grading/review-result.json")
grade = grade_result(
    result,
    assessment="UPHELD",
    assessor="operator",
    note="The approved action completed within its declared scope.",
)
append_grade(Path("examples/grading/grades.jsonl"), grade)
```

Assessments are explicit: `UPHELD`, `OVERTURNED`, or `INCONCLUSIVE`. Anubis
does not infer correctness from an outcome and does not store the raw note.
