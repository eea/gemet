from django.utils.http import is_safe_url
from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout
from django.views.generic import FormView, RedirectView

from gemet.thesaurus.forms import LDAPAuthenticationForm


class LoginView(FormView):
    """
    Provides the ability to login as a user with a username and password
    """
    success_url = '/'
    form_class = LDAPAuthenticationForm
    template_name = 'login.html'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.GET.get(REDIRECT_FIELD_NAME)
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = self.success_url
        return redirect_to


class LogoutView(RedirectView):
    """
    Provides users the ability to logout
    """
    url = '/'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)
