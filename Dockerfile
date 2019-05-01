# We use Debian images because they are considered more stable than the alpine
# ones becase they use a different C compiler. Debian images also come with
# all useful packages required for image manipulation out of the box. They
# however weight a lot, approx. up to 1.5GiB per built image.
FROM python:3.6.6-stretch

RUN useradd npr_poc

WORKDIR /app

# Set default environment variables. They are used at build time and runtime.
# If you specify your own environment variables on Heroku or Dokku, they will
# override the ones set here. The ones below serve as sane defaults only.
#  * PYTHONUNBUFFERED - This is useful so Python does not hold any messages
#    from being output.
#    https://docs.python.org/3.8/using/cmdline.html#envvar-PYTHONUNBUFFERED
#    https://docs.python.org/3.8/using/cmdline.html#cmdoption-u
#  * PYTHONPATH - enables use of django-admin command.
#  * DJANGO_SETTINGS_MODULE - default settings used in the container.
#  * PORT - default port used. Please match with EXPOSE so it works on Dokku.
#    Heroku will ignore EXPOSE and only set PORT variable. PORT variable is
#    read/used by Gunicorn.
#  * WEB_CONCURRENCY - number of workers used by Gunicorn. The variable is
#    read by Gunicorn.
#  * GUNICORN_CMD_ARGS - additional arguments to be passed to Gunicorn. This
#    variable is read by Gunicorn
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=npr_poc.settings.production \
    PORT=8000 \
    WEB_CONCURRENCY=3 \
    GUNICORN_CMD_ARGS="-c gunicorn-conf.py --max-requests 1200 --access-logfile -"

# Port exposed by this container. Should default to the port used by your WSGI
# server (Gunicorn). This is read by Dokku only. Heroku will ignore this.
EXPOSE 8000

# Install operating system dependencies.
RUN apt-get update -y && \
    apt-get install -y apt-transport-https rsync && \
    curl -sL https://deb.nodesource.com/setup_8.x | bash - &&\
    apt-get install -y nodejs &&\
    rm -rf /var/lib/apt/lists/*

# Install ffmpeg
WORKDIR /vendor/ffmpeg
RUN curl -L --silent https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz | tar xJ --strip-components=1
ENV PATH "$PATH:/vendor/ffmpeg"

# Intsall WSGI server - Gunicorn - that will serve the application.
RUN pip install "gunicorn== 19.9.0"

WORKDIR /app/npr_poc/static_src

# Install front-end dependencies.
# TODO: Once new npm LTS version is released, please switch to using "npm ci"
# instead of "npm install" - https://docs.npmjs.com/cli/ci.
COPY --chown=npr_poc ./npr_poc/static_src/package.json ./npr_poc/static_src/package-lock.json ./
RUN npm install

# Install your app's Python requirements.
COPY requirements.txt /
RUN pip install -r /requirements.txt

# Compile static files
COPY --chown=npr_poc ./npr_poc/static_src/ ./
RUN npm run build:prod

# Copy gunicorn config overrides.
COPY gunicorn-conf.py ./

WORKDIR /app

# Copy application code.
COPY --chown=npr_poc . .

# Collect static. This command will move static files from application
# directories and "static_compiled" folder to the main static directory that
# will be served by the WSGI server.
RUN SECRET_KEY=none django-admin collectstatic --noinput --clear

# Don't use the root user as it's an anti-pattern and Heroku does not run
# containers as root either.
# https://devcenter.heroku.com/articles/container-registry-and-runtime#dockerfile-commands-and-runtime
USER npr_poc

# Run the WSGI server. It reads GUNICORN_CMD_ARGS, PORT and WEB_CONCURRENCY
# environment variable hence we don't specify a lot options below.
CMD gunicorn npr_poc.wsgi:application
