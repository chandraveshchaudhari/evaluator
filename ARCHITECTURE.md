# INSTRUCTIONS FOR MIGRATING TO NEW ARCHITECTURE

**DO NOT change ANY existing logic inside existing Python files.
DO NOT rewrite functions.
DO NOT rename variables or change code behavior.
Only reorganize the directory structure and create new wrapper files.**

Perform the following steps **exactly as written**:

---

## 1. Create New Folder Structure (without moving logic yet)

Create these empty folders:

```
instantgrader/core/
instantgrader/executors/
instantgrader/evaluators/base/
instantgrader/reporting/
instantgrader/templates/evaluator_skeleton/
instantgrader/templates/dockerfiles/
```

Do not move any existing file yet.

---

## 2. Extract *existing* evaluator logic into evaluators/python (copy first)

Create folder:

```
instantgrader/evaluators/python/
```

Then **copy** (not move yet) all current evaluator-related files (comparison, grading, test running, student execution logic) into this folder.

Keep directory names and filenames the same.

**Do not change content of any file.**

---

## 3. Extract execution logic into executors/ (copy first)

Create empty files:

```
instantgrader/executors/docker_executor.py
instantgrader/executors/local_executor.py
instantgrader/executors/base_executor.py
instantgrader/core/sandbox_policies.py
```

Add minimal placeholder classes:

```python
class BaseExecutor:
    pass
```

```python
class DockerExecutor(BaseExecutor):
    pass
```

```python
class LocalExecutor(BaseExecutor):
    pass
```

Do **NOT** modify or move current docker execution logic yet.
Do **NOT** import anything existing.
The placeholders must not affect runtime.

---

## 4. Introduce Orchestrator Skeleton (non-functional placeholder)

Create file:

```
instantgrader/core/orchestrator.py
```

Add:

```python
class Orchestrator:
    """
    Placeholder orchestrator. Does NOT change current grading behavior.
    Real logic will be added later.
    """
    pass
```

No imports.
No logic.
Just a placeholder.

---

## 5. Introduce AssignmentLoader, Registry, Models (skeleton only)

Create files:

```
instantgrader/core/assignment_loader.py
instantgrader/core/registry.py
instantgrader/core/models.py
```

Add minimal skeletons only:

### assignment_loader.py

```python
class AssignmentLoader:
    """
    Placeholder. Does not affect existing flows.
    """
    pass
```

### registry.py

```python
class PluginRegistry:
    """
    Placeholder plugin mapping.
    """
    def register(self, assignment_type, config):
        pass

    def get(self, assignment_type):
        return None
```

### models.py

```python
class ExecutionResult:
    """
    Placeholder. Real fields will be populated later.
    """
    pass
```

Again: **no imports**, **no logic**.

---

## 6. Add Evaluator Entrypoint Skeleton (future Docker entrypoint)

Create file:

```
instantgrader/evaluators/base/evaluator_main.py
```

Add placeholder only:

```python
def main():
    """
    Placeholder entrypoint for evaluators.
    Does NOT execute anything yet.
    """
    pass
```

---

## 7. Reporting Skeleton

Create:

```
instantgrader/reporting/reporting_service.py
```

Add:

```python
class ReportingService:
    """
    Placeholder reporting service.
    Does not change existing reporting output.
    """
    pass
```

---

## 8. DO NOT TOUCH these existing components:

* comparison logic
* test running logic
* student execution logic
* docker command logic
* reporting logic
* scoring logic
* evaluator config handling
* CLI logic
* any function bodies

The agent must not alter or optimize any code.

---

## 9. Create Adapter Layer (SAFE integration without breaking anything)

Create:

```
instantgrader/legacy_adapter.py
```

Add:

```python
"""
This module redirects new architecture calls back to the old system.
Nothing inside existing code changes.
"""
def run_grading_with_legacy_system(*args, **kwargs):
    from old_entrypoint import run_grading  # actual import path of your current system
    return run_grading(*args, **kwargs)
```

This ensures that the new architecture exists **without modifying existing behavior**.

---

## 10. Update CLI to optionally call new orchestrator (but default to old)

Modify CLI file (only add new branch, DO NOT remove old logic):

```python
if use_new_architecture_flag:
    from instantgrader.core.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    return orchestrator  # placeholder, safe no-op
else:
    from instantgrader.legacy_adapter import run_grading_with_legacy_system
    return run_grading_with_legacy_system(...)
```

This guarantees nothing breaks.

---

## 11. Freeze All Actual Logic

Before making ANY further change, ensure:

1. tests still pass
2. grading output is unchanged
3. no evaluator behavior changes
4. no Docker build changes
5. no execution flow changes

---

## 12. Stop here (no shifting logic yet)

Future steps (moving logic from legacy into the new architecture) will occur *after* you verify the skeleton does not affect your existing pipeline.

---

# ✔ Summary (for the agent)

1. **Create folder structure**
2. **Copy (not move) evaluator & executor logic into new folders**
3. **Create placeholder classes only**
4. **Add adapter to keep using current system**
5. **Do not change any existing code behavior**
6. **Ensure CLI still uses old system by default**

This gives you the new architecture **without breaking anything**, and allows a safe, incremental migration.
