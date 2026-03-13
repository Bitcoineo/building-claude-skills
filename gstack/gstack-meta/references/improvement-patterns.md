# Improvement Patterns Discovered During Gstack Audit

Patterns discovered while auditing and improving the 8 gstack skills. Each pattern includes the root cause, fix, and prevention rule.

## Pattern 1: Missing Negative Triggers (Universal)

**Root cause:** All 8 original skills had zero negative triggers in their descriptions. This means any adjacent query could activate the wrong skill.

**Why it matters:** The gstack skills are closely related — plan-ceo-review, plan-eng-review, and review all deal with "reviewing" something. Without negative triggers, asking "review this PR" could activate the CEO plan review instead of the code review skill.

**Fix:** Add explicit "Do NOT use for [adjacent task]" to every description, cross-referencing the correct skill.

**Prevention:** Every skill description must include at least one negative trigger naming the most likely misfire target by its skill name.

## Pattern 2: Missing Trigger Phrases (5 of 8 Skills)

**Root cause:** Descriptions explained WHAT the skill does but not WHEN users would invoke it. The description is the gatekeeper — Claude sees only name + description when deciding whether to activate a skill.

**Fix:** Add quoted trigger phrases: "Use when user asks to 'review my plan', 'critique this architecture'..."

**Prevention:** Every description must follow the structure: [WHAT] + [WHEN: trigger phrases] + [WHEN NOT: negatives].

## Pattern 3: Body Near Limit Without Progressive Disclosure (2 Skills)

**Root cause:** plan-ceo-review (484 lines) and retro (429 lines) packed detailed reference tables and templates into the body. The 500-line body limit exists because Claude's instruction-following degrades with excessive context.

**Fix:** Extract tables, templates, JSON schemas, and formulas into `references/` files. Replace inline content with "Consult `references/file.md`" directives.

**Prevention:** Use the progressive disclosure test: "Is this needed every invocation?" If no, move to references/. Tables and templates are almost always reference material.

## Pattern 4: Second-Person Voice Instead of Imperative (plan-ceo-review)

**Root cause:** Instructions like "You are not here to rubber-stamp" read like motivational writing, not executable instructions. Claude responds better to imperative form.

**Fix:** Convert to imperative: "Do not rubber-stamp. Make the plan extraordinary."

**Prevention:** Write SKILL.md instructions as a runbook for Claude to follow, not as a persona description for Claude to inhabit.

## Pattern 5: Rails/Node Specificity Not Declared (2 Skills)

**Root cause:** plan-ceo-review references ActiveRecord, Faraday, Rails.logger in examples. Ship references `bin/test-lane` and `npm run test`. But neither declares its framework dependency.

**Fix:** Add `compatibility` field to frontmatter and note the framework context in the description.

**Prevention:** If a skill's examples or commands assume a specific framework, declare it in the description or compatibility field.

## Pattern 6: No Rollback Guidance (ship)

**Root cause:** The ship skill automates the entire path from code to PR but has no guidance for what happens if the PR breaks production.

**Fix:** Add a Rollback Guidance section covering revert, migration rollback, and fix-forward strategies.

**Prevention:** Any workflow that deploys or ships code should include a "what if it breaks" section.

## Pattern 7: No Error Recovery Guidance (browse)

**Root cause:** The browse skill lists commands but doesn't explain what to do when commands fail (element not found, timeout, empty snapshot).

**Fix:** Add a Common Errors and Recovery table mapping symptoms to causes and recovery steps.

**Prevention:** For tool-orchestration skills, include a troubleshooting table covering the 5 most common failure modes.

## Pattern 8: Ambiguous Navigation Targets (qa)

**Root cause:** Quick mode says "top 5 navigation targets" without defining how to identify them, leaving Claude to guess.

**Fix:** Specify "top 5 links visible on the homepage by DOM order."

**Prevention:** Replace ambiguous instructions with explicit decision criteria. "Handle appropriately" → specific checklist.
