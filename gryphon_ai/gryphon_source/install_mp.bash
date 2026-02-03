#!/bin/bash
# abort on error
set -e

mp_gryphon_path=${HOME}/mp_gryphon
cat <<EOF
********************************************************************************
               Configure Linux/Mac to support Monterey Phoenix
********************************************************************************
Usage: ./install_mp.bash <your OS name>
This script installs packages required by MP Gryphon and installs
MP Gryphon packages under ${mp_gryphon_path}:
    * Trace generator
    * Gryphon
    * Preloaded examples

EOF

# parse required OS parameter
if [ "$1" != "" ]; then
  target_os=$1
else
  echo An OS name is required.  Aborting.
  exit
fi
echo "Press enter to continue..."
read

install_trace_generator() {
  # install or upgrade trace-generator
  if [ ! -d ${mp_gryphon_path}/trace-generator ]
  then
    echo "Installing Trace Generator..."
    mkdir -p $mp_gryphon_path
    cd ${mp_gryphon_path} ; git clone https://gitlab.nps.edu/monterey-phoenix/trace-generator.git
  else
    echo "Upgrading Trace Generator $trace_generator_version..."
    cd ${mp_gryphon_path}/trace-generator ; git pull --ff-only
  fi

  # build trace-generator
  echo "Building trace-generator..."
  cd ${mp_gryphon_path}/trace-generator/RIGAL/rigsc.446/src ; make

  echo "Trace generator build complete."
}

install_gryphon() {
  # install or upgrade Gryphon
  if [ ! -d ${mp_gryphon_path}/gryphon ]; then
    echo "Installing Gryphon..."
    mkdir -p $mp_gryphon_path
    cd $mp_gryphon_path ; git clone https://gitlab.nps.edu/monterey-phoenix/user-interfaces/gryphon.git
  else
    echo "Upgrading Gryphon..."
    cd ${mp_gryphon_path}/gryphon ; git pull --ff-only
  fi
}

install_preloaded_examples() {
  # install or upgrade preloaded examples
  if [ ! -d ${mp_gryphon_path}/preloaded-examples ]; then
    echo "Installing preloaded examples..."
    mkdir -p $mp_gryphon_path
    cd $mp_gryphon_path ; git clone https://gitlab.nps.edu/monterey-phoenix/mp-model-collection/preloaded-examples.git
  else
    echo "Upgrading preloaded examples..."
    cd ${mp_gryphon_path}/preloaded-examples ; git pull --ff-only ;
  fi
}

install_mp_gryphon() {
  install_trace_generator
  install_gryphon
  install_preloaded_examples
}

# install
case $target_os in
ubuntu)
  echo "Updating existing packages..."
  sudo apt-get update
  echo "Installing requisite packages..."
  sudo apt install build-essential
  sudo apt install libc6-dev-i386
  sudo apt install csh
  sudo apt install git
  sudo pip3 install --upgrade pip
  pip3 install PySide6
  pip3 install QDarkstyle
  install_mp_gryphon
  ;;

macos)
  echo "Installing requisite packages..."
  pip3 install --upgrade pip
  pip3 install PySide6
  pip3 install qdarkstyle
  install_gryphon
  install_preloaded_examples
  ;;

gryphon_only)
  echo "Installing Gryphon only..."
  install_gryphon
  install_preloaded_examples
  ;;

*)
  echo Installer for ${target_os} not detected.  Packages not installed.
  exit 1
esac

echo "Installation complete."
echo "Monterey Phoenix is now installed and current."

