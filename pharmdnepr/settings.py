BOT_NAME = 'pharmdnepr'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['pharmdnepr.spiders']
NEWSPIDER_MODULE = 'pharmdnepr.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

ITEM_PIPELINES = ['pharmdnepr.pipelines.PharmdneprPipeline']

CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_SPIDERS = 1
