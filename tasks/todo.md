# Linter setup
- [x] Add `pre-commit`, `black`, `flake8` to `backend/requirements.txt` based on current state. (Omitted to avoid cloud run inclusion, installed locally instead).
- [x] Create `.pre-commit-config.yaml` at the root of the repository.
- [x] Configure `black` and `flake8` hooks in the config file.
- [x] Provide instructions to the user to run `pre-commit install`. (Already ran it).

## Review
- [x] All pre-commit hooks (`black`, `flake8`) pass on the full codebase.
- [x] Documentation ([README.md](file:///home/gozy4/programming/LinkedInPosts/README.md), [lessons.md](file:///home/gozy4/programming/LinkedInPosts/tasks/lessons.md), [architecture_knowledge.md](file:///home/gozy4/programming/LinkedInPosts/tasks/architecture_knowledge.md)) is up to date.
- [x] Fixed all remaining `E501` long line errors manually.
