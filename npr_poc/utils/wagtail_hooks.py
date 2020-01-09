from django.conf import settings
from django.utils.html import format_html_join

from wagtail.core import hooks


@hooks.register("insert_editor_css")
def insert_editor_css():
    return """<style>
        .Draftail-Toolbar {
            background-color: white !important;
            color: #606060 !important;
            border: 1px solid #606060!important;
            border-radius: 3px;
        }
        .Draftail-ToolbarGroup:before {
            content: "";
            display: inline-block;
            width: 0px !important;
            height: 0 !important;
            vertical-align: middle;
            margin: 0 !important;
        }

        .Draftail-ToolbarButton:hover,
        .Draftail-ToolbarButton--active {
            background-color: #eee!important;
            border: 1px solid #ddd!important;
        }

        .Draftail-ToolbarButton[name="READABILITY"] {
            font-weight: 500;
        }
    </style>"""


@hooks.register("insert_editor_js")
def editor_js():
    """ Adds additional JavaScript files or code snippets to the page editor. """
    js_files = [
        "wagtailadmin/js/draftail.js",
        "draftail/api-monkeypatch.js",
        "draftail/readability.js",
        "draftail/word-flags.js",
    ]
    js_includes = format_html_join(
        "\n",
        '<script src="{0}{1}"></script>',
        ((settings.STATIC_URL, filename) for filename in js_files),
    )
    return js_includes
