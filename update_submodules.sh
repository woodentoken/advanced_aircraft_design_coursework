# this script initializes and updates git submodules, then runs 'uv sync'

# this clones the Aviary codebase to the local repository
git submodule update --init --recursive

# this updates the submodules to the latest commit in their respective repositories
git submodule sync

./build_pyoptsparse/build_pyoptsparse.py -d --pip-cmd='uv pip'

# this pulls the latest changes from the remote repositories for each submodule
uv sync
