#!/bin/sh
set -xe

PROJECT_NAME=$1

PROJECT_DIR=/vagrant
VIRTUALENV_DIR=/home/vagrant/.virtualenvs/$PROJECT_NAME

PYTHON=$VIRTUALENV_DIR/bin/python
PIP=$VIRTUALENV_DIR/bin/pip

# Virtualenv setup for project
su - vagrant -c "virtualenv --python=python3 $VIRTUALENV_DIR"

su - vagrant -c "echo $PROJECT_DIR > $VIRTUALENV_DIR/.project"


# Upgrade PIP itself
su - vagrant -c "$PIP install --upgrade pip"

# Upgrade setuptools (for example html5lib needs 1.8.5+)
su - vagrant -c "$PIP install --upgrade six setuptools"

# Install PIP requirements
su - vagrant -c "cd $PROJECT_DIR && $PIP install -r requirements-dev.txt"

# Install Fabric 2
apt-get remove -y fabric
su - vagrant -c "$PIP install Fabric==2.1.3"

# Set execute permissions on manage.py as they get lost if we build from a zip file
chmod a+x $PROJECT_DIR/manage.py


# running migrations here is typically not necessary because of fab pull_data
# su - vagrant -c "$PYTHON $PROJECT_DIR/manage.py migrate --noinput"

# Install Heroku CLI
curl -sSL https://cli-assets.heroku.com/install-ubuntu.sh | sh

# Install AWS CLI
apt-get update -y
apt-get install -y unzip
rm -rf /tmp/awscli-bundle || true
rm -rf /tmp/awscli-bundle.zip || true
curl -sSL "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "/tmp/awscli-bundle.zip"
unzip -q /tmp/awscli-bundle.zip -d /tmp
/tmp/awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws

# Add a couple of aliases to manage.py into .bashrc
cat << EOF >> /home/vagrant/.bashrc
export PYTHONPATH=$PROJECT_DIR
export DJANGO_SETTINGS_MODULE=$PROJECT_NAME.settings.dev
export DATABASE_URL=postgres:///$PROJECT_NAME
export PGDATABASE=$PROJECT_NAME

alias dj="django-admin.py"
alias djrun="dj runserver 0.0.0.0:8000"
alias djrunp="dj runserver_plus 0.0.0.0:8000"

source $VIRTUALENV_DIR/bin/activate
export PS1="[$PROJECT_NAME \W]\\$ "
cd $PROJECT_DIR
EOF

# POSTGRES UPGRADE:
# Once buster box develepment complete, this can be removed.
# https://github.com/wagtail/vagrant-wagtail-base/tree/buster64
PG_VERSION=$(pg_config --version)
if [[ $PG_VERSION == "PostgreSQL 11"* ]] ;
then
    echo "$PG_VERSION already installed"
else
    # Upgrade to postgres 11
    echo "$PG_VERSION found, uninstalling";
    service postgresql stop
    apt-get remove -y --force-yes --purge "^postgresql-.*"

    # https://wiki.postgresql.org/wiki/Apt
    apt-get install -y curl ca-certificates gnupg
    curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
    sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

    apt-get install -y postgresql-11 postgresql-client-11 postgresql-contrib-11
    su - postgres -c "createuser -s vagrant"
fi

# Create database (let it fail because database may exist)
set +e
su - vagrant -c "createdb $PROJECT_NAME"
set -e


# Install node.js and npm
curl -sSL https://deb.nodesource.com/setup_8.x | bash -
apt-get install -y nodejs

# Install ffmpeg
apt-get install -y ffmpeg
