# CodeSecure AI — Structured Finding Extraction Prompt

Given free-form review observations, normalize all items into standard CodeSecure AI structured findings schema.

### Input Observations:
{{raw_observations}}

### Target Schema:
Return ONLY a valid JSON object matching:
```json
{
  "findings": [
    {
      "id": "F001",
      "severity": "Critical|High|Medium|Low|Informational",
      "category": "Category Name",
      "file": "source.cpp",
      "function": "functionName",
      "line": 0,
      "issue": "Concise issue title",
      "evidence": "Specific code or expression",
      "root_cause": "Underlying defect mechanism",
      "recommendation": "Concrete mitigation action",
      "rule": "KB-XXX-000",
      "confidence": 0.90,
      "status": "Open",
      "citations": ["KB-XXX-000"]
    }
  ]
}
```
No markdown wrapping other than the JSON block itself. Ensure all strings are properly escaped.
