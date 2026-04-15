from __future__ import annotations

SYSTEM_PROMPT_BASELINE = """You have a hidden rule for number triples (x,y,z).
The triple (2,4,6) satisfies this rule.

Your goal: discover the rule through testing.

YOU MUST respond in a fenced ```python``` block on EVERY turn, using this EXACT content:
H: lambda x,y,z: <hypothesis>
T: [x, y, z]

STRICT RULES:
1. You MUST provide both H and T on every single turn
2. Use ONLY positive integers from 1 to 1000 (no zero, no negatives, no decimals)
2a. NEVER use 1001 or larger - any value above 1000 is invalid
2b. H MUST be valid Python code of the exact form: lambda x,y,z: <boolean expression>
2c. Use Python operators only: ==, !=, <, <=, >, >=, +, -, *, /, %, and, or, not
2d. NEVER use plain "=" inside H. Equality must be written as "=="
2e. If H is not valid Python lambda syntax, your answer is INVALID
3. NO explanations, commentary, or reasoning in your response
4. NO stopping until maximum turns reached
5. If you respond without a ```python``` block, your response is INVALID
6. If you respond without "T: [...]", your response is INVALID

Example response:
```python
H: lambda x,y,z: x < y < z
T: [5, 10, 15]
```"""

SYSTEM_PROMPT_ADAPTIVE = """You have a hidden rule for number triples (x,y,z).
The triple (2,4,6) satisfies this rule.

Your goal: discover the rule through testing.

YOU MUST respond in a fenced ```python``` block on EVERY turn, using this EXACT content:
H: lambda x,y,z: <hypothesis>
T: [x, y, z]

STRICT RULES:
1. You MUST provide both H and T on every single turn
2. Use ONLY positive integers from 1 to 1000 (no zero, no negatives, no decimals)
2a. NEVER use 1001 or larger - any value above 1000 is invalid
2b. H MUST be valid Python code of the exact form: lambda x,y,z: <boolean expression>
2c. Use Python operators only: ==, !=, <, <=, >, >=, +, -, *, /, %, and, or, not
2d. NEVER use plain "=" inside H. Equality must be written as "=="
2e. If H is not valid Python lambda syntax, your answer is INVALID
3. NO explanations, commentary, or reasoning in your response
4. NO stopping until maximum turns reached
5. If you respond without a ```python``` block, your response is INVALID
6. If you respond without "T: [...]", your response is INVALID

Example response:
```python
H: lambda x,y,z: x < y < z
T: [5, 10, 15]
```

CRITICAL TESTING APPROACH:
- Your hypothesis should explain ALL observed results (both True and False)
- If you get a False result, your hypothesis MUST change to exclude that case
- If you get an unexpected True, your hypothesis MUST expand to include it
- Prefer tests that could prove your current hypothesis wrong, not just confirm it
- Repeatedly proposing triples your current hypothesis already expects to be True is weak testing
- Use boundary cases and contrastive cases that distinguish your current hypothesis from nearby alternatives
- Consider mathematical properties: sums, products, differences, divisibility, remainders (% operator)
- The rule is specific - not all triples satisfy it
- Pay attention to what makes some triples return True and others False"""

SYSTEM_PROMPT_JSON_SUFFIX = """

OUTPUT FORMAT OVERRIDE:
- Return ONLY a JSON object
- The JSON object must have exactly two keys: "hypothesis" and "test"
- "hypothesis" must be a string of the exact form: lambda x,y,z: <boolean expression>
- "test" must be a JSON array of exactly 3 integers
- Do NOT wrap the JSON in markdown or code fences
- Do NOT add explanations or extra keys"""
