# Split test vectors

Cases shared by the Python backend and the TypeScript demo. Both must produce the same results.

- Money is whole pennies (1000 means £10.00).
- Weights are whole numbers or fraction strings such as "1/3". A person is {"fixed": pence, "weight": w}; both are optional (fixed 0, weight 1).
- "expected" is the exact result. "error": "mismatch" means the amounts do not add up to the bill, with the expected "difference" (positive is too much, negative is too little). "error": "invalid" means any other bad input.
