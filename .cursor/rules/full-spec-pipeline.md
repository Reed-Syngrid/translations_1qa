# Full Spec Pipeline
Automation for Speckit workflow.

## Rules
- When I say "full-spec-pipeline: [description]", you must:
  1. Run `/speckit.specify` with the provided [description].
  2. Once `spec.md` is created, immediately run `/speckit.plan`.
  3. Once `plan.md` is created, immediately run `/speckit.tasks`.
  4. Once `tasks.md` is created, run `/speckit.analyze`.
- Do not search the web for local paths.
- Do not stop until all 4 steps are complete or an error occurs.