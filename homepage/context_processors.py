from homepage.models import *


def site_configuration_processor(request):
    return {'site_config': SiteConfiguration.get_solo()}
