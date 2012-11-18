#-*- coding: utf-8 -*-
import datetime
from django.db.models.query_utils import Q
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from django.template import RequestContext
from django_ses import SESBackend
from apps.mailing.emails.models  import Email
from apps.mailing.emails.exceptions import Diffrent_emails, Email_is_empty


def send_email(request, topic, template,
               email = None, data_email = None, sender = None,
               is_send_now = True, user = None, send_by_S3 = False, send_at=None):
    """
    function for sending emails
    @param request:
    @param topic: email topic 
    @param template: template which we use when we render email will be sent
    @param email: User’s email address, to which we want to send email.  If user and email address are not None and “user.email” doesn’t equal email, we get an exception
    @param data_email: variables sent to template defined in rendering template
    @param is_send_now: If value is True then email will be sent immediately else we need to use extra command ./manage.py send_emails
    @param send_at: We use these parameters if we want to send email after the date (e.g. after 11:11 11.11.2012)
    @param sender: please see additional functionalities in documentation
    @return:
    """

    from django.conf import settings
    if not data_email:
        data_email = {}
    data_email['ADDRESS'] = "" 
    if user and 'user' not in data_email:
        data_email['user'] = user

    if user and email:
        if user.email != email:
            raise Diffrent_emails(email)

    if send_at not None and is_send_now is True:
	is_send_now = False
      
    #save email to database


    if user:
        email = user.email
    elif not email:
        raise Email_is_empty

    email_obj = Email(topic=topic, send_at=send_at, is_send_by_S3=send_by_S3, user=user, email=email)

    data_email['email_obj'] = email_obj

    context = RequestContext(request) if request else None

    body = render_to_string(template, data_email, context_instance=context)
    email_obj.body = body

    fail_silently = None
    backend = None
    from_email = settings.MY_MAIL
    if send_by_S3:
        backend='django_ses.SESBackend'
    if sender:
        connection =  get_connection(username=sender.auth_sender,
                                    password=sender.password_sender,
                                    fail_silently=fail_silently, backend = backend)
        from_email = sender.sender
        email_obj.sender = sender

    else:
        connection = None

    if is_send_now:

        email = EmailMessage(subject=topic, body = body, from_email = from_email, to = [email], connection= connection)
        email.content_subtype = "html"
        if file:
            email.attach(file.name, file.read(), "application/pdf")
        email.send()
    else:
        email_obj.is_send = False

    email_obj.save()



def send_non_send_email():
    from settings import MY_MAIL
    emails = Email.objects.filter(Q(is_send = False), (Q(send_at__isnull=True) | Q(send_at__lte=datetime.datetime.now())))
    for email in emails:
        if email.email:
            email_to_user = email.email
        else:
            email_to_user = email.user.email
        email_send = EmailMessage(subject=email.topic, body = email.body, from_email = MY_MAIL, to = [email_to_user], connection= None)
        email_send.content_subtype = "html"
        email_send.send()
        email.is_send = True
        email.save()

