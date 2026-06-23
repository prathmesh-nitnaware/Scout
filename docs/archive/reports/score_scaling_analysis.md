# Score Floor Investigation

## Findings
1. **Why was 0.20 introduced?** It was carried over from the original baseline TF-IDF script which scaled all cosine similarities between 0.20 and 0.99 to make them 'look' like real scores.
2. **Is the validator requiring it?** No. The validator only checks for non-increasing scores between rows.
3. **Does it change ranking order?** No. The sort happens before the floor is applied.
4. **Did any top 100 candidate actually hit the floor?** The minimum score in the top 100 is 0.5975, which is well above 0.20. The floor was mathematically irrelevant to the top 100.

## Recommendation
Remove the artificial bounds entirely. Let the true scores (0.0000 - 1.0000) represent the pure ranking fidelity.
