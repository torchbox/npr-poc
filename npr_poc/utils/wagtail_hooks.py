import json

from django.shortcuts import render
from django.urls import path
from django.utils.text import slugify
from django.utils.html import format_html

from wagtail.admin.action_menu import PageActionMenu
from wagtail.admin.views.pages import get_valid_next_url_from_request
from wagtail.core import hooks

from . import views


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
    </style>"""
