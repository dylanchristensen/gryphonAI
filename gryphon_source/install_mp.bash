#!/bin/bash
# abort on error
set -e

mp_gryphon_path=${HOME}/mp_gryphon
cat <<EOF
********************************************************************************
          Configure Linux/Mac to support Monterey Phoenix - Gryphon
********************************************************************************
Usage: ./install_mp.bash <configuration>
Configuration options are:

    * ubuntu - Installs:
               trace-generator and required system packages,
               Gryphon and required pip packages,
               preloaded examples

    * ubuntu_server - Installs:
               trace-generator and required system packages,
               Gryphon and required pip packages,

    * macos - Installs:
               Gryphon and required pip packages,
               preloaded examples

The trace generator, Gryphon, and preloaded examples are installed under ${mp_gryphon_path}.

EOF

# parse required OS parameter
if [ "$1" != "" ]; then
  target_os=$1
else
  echo A configuration option is required.  Aborting.
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

install_ubuntu_gryphon_launcher() {
  echo "Adding Gryphon launcher to desktop..."
  launcher_path="${HOME}/Desktop/Gryphon.desktop"
  cat <<EOF > ${launcher_path}
[Desktop Entry]
Version=1.0
Type=Application
Name=Gryphon
Comment=
Exec=python3 mp.py
Icon=${mp_gryphon_path}/gryphon/python/resources/icons/MP-logo-small-blue.png
Path=${mp_gryphon_path}/gryphon/python
Terminal=false
EOF
  chmod a+x ${launcher_path}
}

# install a configuration on a target OS
case $target_os in
ubuntu_server)
  echo "Updating existing packages..."
  sudo apt-get update
  echo "Installing requisite packages..."
  sudo apt install build-essential
  sudo apt install libc6-dev-i386
  sudo apt install csh
  sudo apt install git
  install_trace_generator
  ;;

ubuntu)
  echo "Updating existing packages..."
  sudo apt-get update
  echo "Installing requisite packages..."
  sudo apt install build-essential
  sudo apt install libc6-dev-i386
  sudo apt install csh
  sudo apt install git
  sudo apt install python3-pip
  pip3 install --upgrade pip
  pip3 install PySide6
  pip3 install pyqtdarktheme
  pip3 install pyspellchecker
  install_trace_generator
  install_gryphon
  install_preloaded_examples
  install_ubuntu_gryphon_launcher
  ;;

macos)
  echo "Installing requisite packages..."
  pip3 install --upgrade pip
  pip3 install PySide6
  pip3 install pyqtdarktheme
  pip3 install pyspellchecker
  install_gryphon
  install_preloaded_examples
  ;;

*)
  echo Error: Configuration ${target_os} is not recognized.  Aborting.
  exit 1
esac

echo "Monterey Phoenix - Gryphon ${target_os} Installation complete."

