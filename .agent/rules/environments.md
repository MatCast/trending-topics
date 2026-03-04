---
trigger: always_on
---

## Python Environments
- **Environment Tool**: The user uses `virtualenvwrapper` to manage python versions.
- **Workspace Environment**: The environment for this project is named `linkedin_posts`.
- **Command References**:
  - To activate: `workon linkedin_posts`
  - To deactivate: `deactivate`
- **Agent Rule**: Before running any custom python commands or installing requirements during the session, ensure you are using the virtual environment paths, such as `~/.virtualenvs/linkedin_posts/bin/python` or `/home/gozy4/.virtualenvs/linkedin_posts/bin/pip`.