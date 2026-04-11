# Task Validation Fix Plan
Status: COMPLETE ✓

## Step 1: Fix openenv.yaml ✅
- [✓] Fixed duplicate grader keys
- [✓] Added enabled: true for each of 4 tasks
- [✓] tasks.count: 4

## Step 2: Add explicit grader functions in grader.py ✅
- [✓] keyword_grader, entity_grader, decision_grader, triage_grader implemented
- [✓] grade_response now dispatches by task['grader']

## Step 3: Update inference.py ✅
- [✓] grader_by_task uses t["grader"] directly

## Step 4: Test ✅
- [✓] docker build successful (metaxscaler:latest)
- [✓] inference.py logic verified (API key needed for full run)

## Next: Resubmit validation. Cleanup unnecessary files after success.


