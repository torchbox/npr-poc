from wagtail.api.v2.endpoints import BaseAPIEndpoint
from wagtail.api.v2.filters import FieldsFilter, OrderingFilter, SearchFilter
from wagtail.api.v2.serializers import BaseSerializer

from ..models import AudioMedia


class AudioMediaAPIEndpoint(BaseAPIEndpoint):
    base_serializer_class = BaseSerializer
    filter_backends = [FieldsFilter, OrderingFilter, SearchFilter]
    body_fields = BaseAPIEndpoint.body_fields + ['title', 'duration', 'bitrate', 'sample_rate', 'channels', 'mime_type']
    meta_fields = BaseAPIEndpoint.meta_fields + ['media_file']
    listing_default_fields = BaseAPIEndpoint.listing_default_fields + ['title', 'media_file']
    nested_default_fields = BaseAPIEndpoint.nested_default_fields + ['title', 'media_file']
    name = 'media'
    model = AudioMedia
