from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout
from django.utils.http import is_safe_url
from django.views.generic import FormView, RedirectView

from gemet.thesaurus.forms import LDAPAuthenticationForm

# For some reason, FORCE_SCRIPT_NAME doesn't get prepended by default
# TODO Investigate this problem
ROOT_URL = (settings.FORCE_SCRIPT_NAME or '') + '/'


class LoginView(FormView):
    """
    Provides the ability to login as a user with a username and password
    """
    success_url = ROOT_URL
    form_class = LDAPAuthenticationForm
    template_name = 'login.html'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.GET.get(REDIRECT_FIELD_NAME)
        if not is_safe_url(url=redirect_to, allowed_hosts=settings.ALLOWED_HOSTS):
            redirect_to = self.success_url
        return redirect_to


class LogoutView(RedirectView):
    """
    Provides users the ability to logout
    """
    url = ROOT_URL

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)
