from django.template.response import TemplateResponse
from apps.mailing.emails.models import Email

def show_email(request, key):
    email = Email.get_by_key(key)
    return TemplateResponse(request, 'emails/show_email.html', locals())

