# NPR POC Wagtail site

This site is not production-ready! It is intended to demonstrate a set of site-specific features including custom review workflows, both server-rendered and headless page serving, import from Google docs, selection of content from NPR APIs, automatic audio transcription, podcast management and editor guides.

# Setting up a local build

This repository includes a Vagrantfile for running the project in a Debian VM and
a fabfile for running common commands with Fabric.

To set up a new build:

``` bash
git clone https://github.com/torchbox/npr-poc.git
cd npr_poc
vagrant up
cp npr_poc/settings/local.py.example npr_poc/settings/local.py
vagrant ssh
```

Then, within the SSH session:

``` bash
dj migrate
dj createsuperuser
djrun
```

This will make the site available on the host machine at: http://127.0.0.1:8000/

# Front-end assets

To build front-end assets you'll need to run the following commands:

 ```bash
cd npr_poc/static_src/
npm install
npm run build
```

After any changes to CSS or JavaScript you will need to run the build command again, either in the VM or on your host machine. See the [Front-end tooling docs](npr_poc/static_src/README.md) for further details.


## Deployment
Don't commit static assets, which should be automatically generated on deployment. 
The command used to generate the production version of static files is `npm run build:prod`.

# Servers
The VM should come preinstalled with Fabric, Heroku CLI and AWS CLI.

## Login to Heroku
Please log in to Heroku before executing any commands for servers hosted there
using the `heroku login -i` command. You have to do it both in the VM and your
host machine if you want to be able to use it in both places.

## Pulling data

To populate your local database with the content of staging/production:

``` bash
fab pull-dev-data
fab pull-staging-data
fab pull-production-data
```

To fetch images and other media:

``` bash
fab pull-dev-media
fab pull-staging-media
fab pull-production-media
```

To fetch only original images, with no extra media files and no renditions:

``` bash
fab pull-dev-images
fab pull-staging-images
fab pull-production-images
```

## Deployments

To deploy the site to dev/staging/production:


``` bash
fab deploy-dev
fab deploy-staging
fab deploy-production
```

## Connect to the shell

To open the shell of the servers.

```bash
fab dev-shell
fab staging-shell
fab production-shell
```

## Pushing database and media files

Please be aware executing those commands is a possibly destructive action. Make
sure to take backups.

If you want to push your local database to the servers.

```bash
fab push-dev-data
fab push-staging-data
fab push-production-data
```

Or if you want to push your local media files.

```bash
fab push-dev-media
fab push-staging-media
fab push-production-media
```

## Scheduled tasks

When you set up a server you should make sure the following scheduled tasks are set.


* `django-admin publish_scheduled_pages` - every 10 minutes or more often. This is necessary to make publishing scheduled pages work.
* `django-admin update_index` - once a day  (not necessary, but useful to make sure search index stays intact).

## Deleting reviews

`heroku run python manage.py shell -a npr-poc`

```
from wagtail_review.models import Review
for r in Review.objects.all(): r.delete()
```
