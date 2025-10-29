# Implementation Plans

This directory contains detailed implementation plans for ONI Save Parser example tools.

## Available Plans

All plans follow Test-Driven Development (TDD) approach with bite-sized tasks (2-5 minutes each).

### High Priority

1. **[Duplicant Analyzer](2025-10-30-duplicant-analyzer.md)** ⭐
   - Status: Planned
   - Complexity: Medium
   - Extract duplicant name, traits, skills, stress, health, location, tasks
   - 7 tasks, ~35-50 minutes

2. **[Resource Counter](2025-10-30-resource-counter.md)** ⭐
   - Status: Planned
   - Complexity: High
   - Count materials in storage, on ground, in pipes
   - 4 tasks, ~20-30 minutes (basic version)

3. **[Power Grid Analyzer](2025-10-30-power-grid-analyzer.md)** ⭐
   - Status: Planned
   - Complexity: High
   - Analyze generators, batteries, consumers, production vs consumption
   - 4 tasks, ~20-30 minutes (basic version)

4. **[Colony Statistics Dashboard](2025-10-30-colony-dashboard.md)** ⭐
   - Status: Planned
   - Complexity: Medium
   - Overview of duplicants, food, oxygen, power, morale
   - 5 tasks, ~25-35 minutes

### Medium Priority

5. **[Critter/Plant Tracker](2025-10-30-critter-plant-tracker.md)**
   - Status: Planned
   - Complexity: Medium
   - Count ranched critters and farmed plants
   - 5 tasks, ~25-35 minutes

6. **[Save File Differ](2025-10-30-save-differ.md)**
   - Status: Planned
   - Complexity: High
   - Compare two saves to show changes
   - 5 tasks, ~30-40 minutes

### Low Priority

7. **[Base Layout Exporter](2025-10-30-base-layout-exporter.md)**
   - Status: Planned
   - Complexity: Medium
   - Export coordinates of tiles/buildings for visualization
   - 5 tasks, ~25-35 minutes

## Using These Plans

### Option 1: Subagent-Driven Development (Recommended)

Execute plans in your current session with code review between tasks:

1. Use the `superpowers:subagent-driven-development` skill
2. Dispatch fresh subagent for each task
3. Review code between tasks
4. Fast iteration with quality gates

### Option 2: Parallel Session Execution

Execute plans in a separate session with batch processing:

1. Open new Claude Code session in this worktree
2. Use the `superpowers:executing-plans` skill
3. Point to plan file
4. Execute tasks in batches with review checkpoints

## Plan Structure

Each plan contains:

- **Goal**: One-sentence description
- **Architecture**: 2-3 sentence approach
- **Tech Stack**: Key technologies
- **Tasks**: Bite-sized TDD tasks
  - Step 1: Write failing test
  - Step 2: Run test to verify it fails
  - Step 3: Implement minimal code
  - Step 4: Run test to verify it passes
  - Step 5: Commit
- **Verification Checklist**: Final checks
- **Future Enhancements**: Next iteration ideas

## Development Principles

All plans follow:

- **TDD**: Test first, verify failure, implement, verify success
- **DRY**: Don't Repeat Yourself
- **YAGNI**: You Aren't Gonna Need It (build what's needed now)
- **Frequent Commits**: Commit after each passing test
- **Bite-Sized Tasks**: 2-5 minutes per step

## Progress Tracking

Update `TOOLS_ROADMAP.md` when completing tools:

- Change status from "Planned" to "Complete"
- Add test count and coverage
- Add usage examples
- Move to "Completed Tools" section

## Creating New Plans

To create a new plan:

1. Use `superpowers:writing-plans` skill
2. Save to `docs/plans/YYYY-MM-DD-feature-name.md`
3. Follow the required header format
4. Include complete code in plan (not "add validation")
5. Use exact file paths
6. Include exact commands with expected output
7. Add to this README

## Questions?

- Check `TOOLS_ROADMAP.md` for feature specifications
- Review existing plans as templates
- See `examples/geyser_info.py` as completed example
