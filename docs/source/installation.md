````markdown
# Installation

This page explains how to install InstantGrade and prepare your environment for Docker-backed grading.

## Install from PyPI

The easiest way to install InstantGrade is from PyPI:

```bash
python3 -m pip install instantgrade
```

After installation you can run the CLI `instantgrade` or import the package in Python:

```python
from instantgrade import Evaluator
```

## Development installation

To work on the code locally (editable install):

```bash
git clone https://github.com/chandraveshchaudhari/instantgrade.git
cd evaluator
python3 -m pip install -e .
```

This installs the package in "editable" mode so local changes to `src/` are reflected immediately.

## Docker (recommended for grading notebooks)

InstantGrade executes student notebooks inside a Docker container by default. This provides consistent Python environments and prevents user code from affecting the host system.

- Install Docker Desktop (macOS/Windows): https://www.docker.com/products/docker-desktop
- Or install Docker Engine on Linux: https://docs.docker.com/engine/install/

After installation, verify Docker is available:

```bash
docker --version
```

If you plan to use Docker-backed grading (recommended for production or reproducible results), ensure the Docker daemon is running before invoking grading.

### Avoiding stale Docker images after an upgrade

When users upgrade InstantGrade (for example after `pip install -U instantgrade`), previously-built Docker images (e.g. `instantgrade:latest`) on their machine may be out of sync with the new code. This can lead to errors such as `ModuleNotFoundError` inside the container.

To avoid stale-image problems, do one of the following after upgrading:

1. Build the repository-specific image (recommended):

```bash
python tools/docker_build_image.py
# or force rebuild
python tools/docker_build_image.py --force
```

This helper builds a docker image tagged with the current git commit short SHA and also tags it `instantgrade:latest` for convenience.

2. Let the runtime rebuild automatically (one-off):

```bash
instantgrade_FORCE_REBUILD=1 instantgrade --solution sample_solutions.ipynb --submissions ./submissions/
```

3. Developer fast-iteration: bind-mount the `src/` directory into your container while developing so you do not need to rebuild for small changes.

## Optional extras

- For Excel-specific advanced features, install `xlwings`:

```bash
python3 -m pip install xlwings
```

- For development tools and tests:

```bash
python3 -m pip install -e .[dev]
```

## Next steps

- See the Quick Start: `docs/quickstart` (or the website) for an end-to-end example.
- If you're packaging a release, bump the version in `pyproject.toml`, tag a release on GitHub, and optionally build/publish the docker image in CI.

````
