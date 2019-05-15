import datetime
import json
from io import StringIO
from json.decoder import JSONDecodeError
from sys import stdout
from urllib.parse import urlsplit, urlunsplit

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import QueryDict
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from django.utils.text import slugify

import requests
from cryptography.fernet import Fernet

from .utils import LineBreakWriter


def import_from_url(importer_class, importer_options, **options):
    source_url = options['source']
    urlparts = urlsplit(source_url)
    querydict = QueryDict(urlparts.query, mutable=True)
    latest_page = start_page = int(querydict['page'])
    success = True
    error_msg = ""
    start_time = timezone.now()
    importer_class = import_string(importer_class)

    task_description = (
        f"{importer_class.description} (pages {start_page}–{options['stoppage']}) import"
    )
    stdout.write(f"[Importer] Starting {task_description}" + '\n')

    if options['recipients'] or options['outfile']:
        attachment = StringIO()
        importer_options['stdout'] = LineBreakWriter(attachment)
        if not options['plaintext']:
            try:
                fernet = Fernet(settings.DATA_MIGRATIONS_LOG_ENCRYPTION_KEY.encode())
            except Exception as e:
                error_msg += "Error with encryption\n"
                error_msg += (str(e) + '\n')
                success = False
    else:
        importer_options['stdout'] = LineBreakWriter(stdout)

    session = requests.Session()
    if (settings.DATA_MIGRATIONS_BASIC_AUTH_USERNAME and
            settings.DATA_MIGRATIONS_BASIC_AUTH_PASSWORD):
        stdout.write("[Importer] Setting basic HTTP auth credentials" + '\n')
        session.auth = (
            settings.DATA_MIGRATIONS_BASIC_AUTH_USERNAME,
            settings.DATA_MIGRATIONS_BASIC_AUTH_PASSWORD
        )
    if (settings.DATA_MIGRATIONS_SOURCE_USERNAME and
            settings.DATA_MIGRATIONS_SOURCE_PASSWORD):
        stdout.write("[Importer] Logging in" + '\n')
        # log in to the Drupal site
        source_root_url = urlunsplit((urlparts.scheme, urlparts.netloc, '',
                                      '', ''))
        session.post(source_root_url, data={
            'name': settings.DATA_MIGRATIONS_SOURCE_USERNAME,
            'pass': settings.DATA_MIGRATIONS_SOURCE_PASSWORD,
            'form_id': 'user_login_block'
        })

    response = session.get(source_url)
    try:
        data = json.loads(response.content)
    except JSONDecodeError as e:
        error_msg += "Error fetching data\n"
        error_msg += (str(e) + '\n')
        data = {}
        success = False

    importer = importer_class(data, **importer_options)

    if success and data:
        while importer.get_iterator():  # (test for data)
            page_number = int(querydict['page'])
            if options['stoppage'] and page_number > options['stoppage']:
                stdout.write(f"[Importer] Stop page exceeded at page {querydict['page']}" + '\n')
                break
            latest_page = page_number

            msg = f"Processing page {querydict['page']}"
            if options['outfile'] or options['recipients']:
                attachment.write(msg + '\n')
            else:
                stdout.write("[Importer]" + msg + '\n')

            importer.process()

            querydict['page'] = page_number + 1
            source_url = urlunsplit((urlparts.scheme, urlparts.netloc,
                                    urlparts.path, querydict.urlencode(),
                                    urlparts.fragment))
            if options['verbosity'] > 1:
                msg = f"Fetching data from {source_url}"
                if options['outfile'] or options['recipients']:
                    attachment.write(msg + '\n')
                else:
                    stdout.write("[Importer]" + msg + '\n')
            response = session.get(source_url)
            importer.source_data = json.loads(response.content)
        else:
            stdout.write(f"[Importer] No more data: page {querydict['page']}" + '\n')

    if error_msg:
        stdout.write(error_msg)

    end_time = timezone.now()
    duration = end_time - start_time
    duration = duration - datetime.timedelta(microseconds=duration.microseconds)

    if options['outfile'] or options['recipients']:
        attachment.seek(0)
        if options['plaintext']:
            file_content = attachment.read()
            content_type = 'text/plain'
            file_extension = 'txt'
        else:
            file_content = fernet.encrypt(attachment.read().encode()).decode()
            content_type = 'application/octet-stream'
            file_extension = 'txt.enc'

    if options['outfile']:
        with open(options['outfile'], 'w') as outfile:
            outfile.write(file_content)

    elif options['recipients']:
        body = render_to_string('data_migration/email/import_report.txt',
                                context={
                                    'description': importer.description,
                                    'success': success,
                                    'error_msg': mark_safe(error_msg),
                                    'start_time': start_time,
                                    'end_time': end_time,
                                    'duration': duration,
                                    'start_page': start_page,
                                    'end_page': latest_page,
                                    'site_name': settings.WAGTAIL_SITE_NAME,
                                })
        message = EmailMessage(
            f'[settings.WAGTAIL_SITE_NAME] {task_description} {success and "complete" or "failed"}',
            body,
            settings.SERVER_EMAIL,
            options['recipients'],
        )

        if success:
            message.attach(
                f'{slugify(importer.description)}-import_{start_page}-{latest_page}.{file_extension}',
                file_content,
                content_type,
            )
        stdout.write(f"[Importer] Emailing report to {' '.join(options['recipients'])}\n")
        message.send()

    if success:
        stdout.write(f"[Importer] {task_description} completed in {duration}\n")
    else:
        stdout.write(f"[Importer] {task_description} failed in {duration}\n")
