import json

from rest_framework import status, serializers
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from wagtail.api.v2.endpoints import PagesAPIEndpoint
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.serializers import PageSerializer, StreamField
from wagtail.documents.api.v2.endpoints import DocumentsAPIEndpoint
from wagtail.images.api.v2.endpoints import ImagesAPIEndpoint

from npr_poc.news.models import NewsPage
from npr_poc.utils.api import PagePreviewAPIEndpoint
from npr_poc.podcasts.api.endpoints import MediaAPIEndpoint
from npr_poc.utils.google import html_to_stream_data

api_router = WagtailAPIRouter('wagtailapi')

api_router.register_endpoint('pages', PagesAPIEndpoint)
api_router.register_endpoint('images', ImagesAPIEndpoint)
api_router.register_endpoint('documents', DocumentsAPIEndpoint)
api_router.register_endpoint('media', MediaAPIEndpoint)
api_router.register_endpoint('page_preview', PagePreviewAPIEndpoint)


class FancyStreamFieldSerializer(StreamField):
    def to_internal_value(self, data):
        body = html_to_stream_data(data)
        return json.dumps(body)


class NewsPageSerializer(PageSerializer):
    author = serializers.StringRelatedField()
    categories = serializers.StringRelatedField()
    body = FancyStreamFieldSerializer()
    tags = serializers.StringRelatedField()

    class Meta:
        model = NewsPage
        fields = ('title', 'date', 'body', 'summary', 'author', 'categories', 'tags')

    meta_fields = []
    child_serializer_classes = {}

    def create(self, validated_data):
        page = self.Meta.model(**validated_data)

        return page


class StorifyAPIEndpoint(ListCreateAPIView):
    serializer_class = NewsPageSerializer
    page_size = 20

    def get_queryset(self):
        return NewsPage.objects.descendant_of(self.request.site.root_page)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()
        parent = self.get_parent()
        parent.add_child(instance=instance)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_parent(self):
        return NewsPage.objects.descendant_of(self.request.site.root_page, inclusive=True).first().get_parent()
