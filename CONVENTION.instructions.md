---
applyTo: "*"
---
# Startr Development Workflow

## Core Principles

Every development task follows the **Plan-Document-Execute-Verify** cycle:

0. Zeroth Principle: **Follow the Standards**
  - **DRY** - Don't Repeat Yourself (ever in Code)
  - **KISS** - Keep It Simple, Stupid
1. **Plan** - Add to TODO.md before doing any work
2. **Document** - Update docs and README as needed
3. **Execute** - Implement changes following standards
4. **Verify** - Test, commit, and check off completed items

## Standard Operating Procedure

### Before Starting Any Work

**ALWAYS add to TODO.md first:**

```markdown
## [Category] TODOs
- [ ] **[Task Name]**: Brief description
  - [ ] Subtask 1
  - [ ] Subtask 2
  - [ ] Test/verify step
  - [ ] Documentation update
```

**NEVER start work without:**
- Adding the task to TODO.md
- Getting approval for significant changes
- Understanding the complete scope

### Planning Requirements

For each task, define:
- **Scope** - What exactly needs to be done
- **Dependencies** - What must be completed first
- **Testing** - How to verify it works
- **Documentation** - What docs need updates


### **During Development**
- Follow coding standards and conventions
- Write clear, concise commit messages
- **ALWAYS USE UV** for python isolation and dependency management
- **ALWAYS USE BUN** for JavaScript/TypeScript projects
- **ALWAYS USE USER STORIES** for version control and collaboration
  - Example: `As a [type of user], I want [an action] so that [a benefit/a value]`
  - Break down large tasks into smaller, manageable subtasks


## See the [DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md) for more details.

## Environment Management

**This project uses autoenv** to automatically load environment variables from `.env` when you `cd` into the project directory. No need to manually source or export variables.

### Setup
1. Install autoenv (if not already installed): `brew install autoenv` (macOS)
2. Add to your shell: `echo "source $(brew --prefix autoenv)/activate.sh" >> ~/.zshrc`
3. Create `.env` from `.env.example` and add your `SAGE_AUTH_TOKEN`
4. Simply `cd` into the project directory - variables load automatically