"""
WSGI config for godeyes project.

It exposes the WSGI callable as a modules-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'godeyes.settings')

application = get_wsgi_application()
