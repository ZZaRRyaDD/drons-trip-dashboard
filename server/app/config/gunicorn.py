from multiprocessing import cpu_count

from app.config.utils import get_settings

settings = get_settings()
bind = f'{settings.APP_HOST}:{settings.APP_PORT}'
workers = cpu_count() * 2 + 1
logconfig_json = 'log_conf.json' # pylint: disable=invalid-name
worker_class = 'uvicorn.workers.UvicornWorker' # pylint: disable=invalid-name
timeout = 300  # pylint: disable=invalid-name
