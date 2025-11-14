# install libraries
sudo apt update
sudo apt upgrade
sudo apt install -y build-essential pkg-config
sudo apt install -y pkg-config gfortran libblas-dev liblapack-dev
sudo apt install -y coinor-libipopt-dev
sudo apt install python3-tk

# this script initializes and updates git submodules, then runs 'uv sync'

# this clones the Aviary codebase to the local repository
git submodule update --init --recursive

# this updates the submodules to the latest commit in their respective repositories
git submodule sync

./build_pyoptsparse/build_pyoptsparse.py -d --pip-cmd='uv pip'

# this pulls the latest changes from the remote repositories for each submodule
uv sync
