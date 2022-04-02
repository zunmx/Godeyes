"""godeyes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from . import view
import View.godeyes.view as views
from django.views.generic.base import RedirectView
from .settings import STATIC_URL

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', view.index, name="login"),
    path('\\', view.index, name="login"),
    path('login/', view.login, name="login"),
    path('install/', view.install, name="install"),
    path('manager/', view.manager, name="manager"),
    path('manager/get_data', view.get_data, name='index'),
    path('manager/set_data', view.set_data, name='index'),
    path('manager', view.manager, name="manager"),
    path('modifyAccount', view.modAccount, name="modifyAccount"),
    path('modifyAccount.do/', view.modifyAccountDo, name="modifyAccount"),
    path('logout', view.logout, name="logout"),
    path('logout/', view.logout, name="logout"),
    path('manager/dashBoard', view.dashBoard, name='dashBoard'),
    path('manager/scanner', view.scanner, name='scanner'),
    path('manager/portSettings', view.portSettings, name='scanner'),
    path('manager/requestConstructor', view.requestConstructor, name='respConst'),
    path('manager/crackRules', view.crackRules, name='crackRules'),
    path('manager/dataManager', view.dataManager, name='dataManager'),
    path('manager/ipTableManager', view.ipTableManager, name='dataManager'),
    path('manager/fingerPrint', view.fingerPrint, name='dataManager'),
    path('manager/license', view.license, name='license'),
    path('manager/Disclaimer', view.Disclaimer, name='Disclaimer'),
    path('manager/help', view.help, name='help'),
    path('manager/userManager', view.userManager, name='userManager'),
    path('manager/scannerLog', view.scannerLog, name='scannerLog'),
    path('manager/systemLog', view.systemLog, name='systemLog'),
    path('manager/systemConfig', view.systemConfig, name='systemConfig'),
    path('manager/ClearData', view.ClearData, name='ClearData'),
    path('manager/donate', view.donate, name='ClearData'),
    path(r'favicon.ico', RedirectView.as_view(url=STATIC_URL + r'imgs/logo.ico')),
]
handler404 = views.errorPage
handler500 = views.errorPage
handler403 = views.errorPage


