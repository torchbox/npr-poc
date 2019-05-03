from wagtail.api.v2.endpoints import PagesAPIEndpoint
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.documents.api.v2.endpoints import DocumentsAPIEndpoint
from wagtail.images.api.v2.endpoints import ImagesAPIEndpoint

from npr_poc.utils.api import PagePreviewAPIEndpoint
from npr_poc.podcasts.api.endpoints import MediaAPIEndpoint

api_router = WagtailAPIRouter('wagtailapi')

api_router.register_endpoint('pages', PagesAPIEndpoint)
api_router.register_endpoint('images', ImagesAPIEndpoint)
api_router.register_endpoint('documents', DocumentsAPIEndpoint)
api_router.register_endpoint('media', MediaAPIEndpoint)
api_router.register_endpoint('page_preview', PagePreviewAPIEndpoint)
