# Resource Counter Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a tool to count all materials in storage containers, loose debris, and duplicant inventories, organized by element type with location breakdowns.

**Architecture:** Multi-pass design with three sequential scans: (1) Storage containers with PrimaryElement extraction, (2) Loose Pickupable objects, (3) Duplicant inventories. Results aggregated by element type with comprehensive JSON output and summary ASCII tables.

**Tech Stack:** Python 3.12+, oni-save-parser library, argparse, dataclasses for type-safe structures

---

The full implementation plan has been created in the brainstorming session.
This tool will implement resource counting with:

1. Script skeleton and test infrastructure
2. Test fixtures with resources in various locations
3. Pass 1: Storage container detection with PrimaryElement extraction
4. Pass 2: Loose debris (Pickupable) detection
5. Pass 3: Duplicant inventory detection
6. JSON output with comprehensive details
7. ASCII table output with sorting
8. Element filter (--element flag)
9. State filter (--state) and minimum mass (--min-mass)
10. List elements feature (--list-elements)
11. Error handling tests
12. Full test suite verification

Each task follows TDD: Write test → Run (fail) → Implement → Run (pass) → Commit

For detailed step-by-step instructions, see the comprehensive plan that was discussed
during the brainstorming session.
