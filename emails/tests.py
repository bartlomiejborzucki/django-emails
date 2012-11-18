#-*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import mail
import time

from apps.mailing.emails.utils import send_email, send_non_send_email
from testing.utils import RequestMock
from apps.mailing.emails.models import Email, Sender
from apps.mailing.emails.exceptions import Diffrent_emails, Email_is_empty


class EmailSendTestCase(TestCase):
    """
        Funkcja sprawdzająca czy można wysyłać maila
    """

    def setUp(self):
        requestMock = RequestMock()
        self.request = requestMock.get_request_mock()
        self.user = User.objects.create_user("Test",email= "user@example.com", password = "test")


    def test_save_email_in_database_non_register_user(self):
        """
            Test sprawdzający czy można zapisać email do bazy danych
        """
        topic = u"Email_testowy"
        data_email = {}
        send_email(self.request, topic, template="emails/emails/base_email.html", data_email = {}, is_send_now = False,
                    email="test@example.com" )

        email_db = Email.objects.get(id = 1)
        self.assertEqual(Email.objects.count(), 1, msg=u"Liczba maili powinna być 1")
        self.assertEqual(email_db.is_send, False, msg = u"Wiadomość nie ma być wysłana")
        self.assertEqual(email_db.is_send_by_S3, False, msg = u"Nie wysyłamy maila przez Amazona")
        self.assertEqual(email_db.email, "test@example.com", msg = u"Sprawdzenie maila")
        self.assertEqual(email_db.topic, u"Email_testowy", msg = u"Sprawdzenie tematu")
        self.assertEqual(email_db.sender, None, msg = u"Wysyłamy przez domyślny email")


        send_email(self.request, topic, template="emails/emails/base_email.html", data_email = {}, is_send_now = True,
                    email="test@example.com" )

        email_db = Email.objects.get(id = 2)
        self.assertEqual(Email.objects.count(), 2, msg=u"Liczba maili powinna być 1")
        self.assertEqual(email_db.is_send, True, msg = u"Wiadomość ma być wysłana")
        self.assertEqual(email_db.is_send_by_S3, False, msg = u"Nie wysyłamy maila przez Amazona")
        self.assertEqual(email_db.email, "test@example.com", msg = u"Sprawdzenie maila")
        self.assertEqual(email_db.topic, u"Email_testowy", msg = u"Sprawdzenie tematu")
        self.assertEqual(email_db.sender, None, msg = u"Wysyłamy przez domyślny email")
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, topic)


    def test_save_email_in_database_register_user(self):
        """
            Test sprawdzający czy można zapisać email do bazy danych
        """
        topic = u"Email_testowy"
        data_email = {}

        send_email(self.request, topic, template="emails/emails/base_email.html", user = self.user, data_email = {}, is_send_now = False)

        email_db = Email.objects.get(id = 1)
        self.assertEqual(Email.objects.count(), 1, msg=u"Liczba maili powinna być 1")
        self.assertEqual(email_db.is_send, False, msg = u"Wiadomość nie ma być wysłana")
        self.assertEqual(email_db.is_send_by_S3, False, msg = u"Nie wysyłamy maila przez Amazona")
        self.assertEqual(email_db.email, "user@example.com", msg = u"Sprawdzenie maila")
        self.assertEqual(email_db.topic, u"Email_testowy", msg = u"Sprawdzenie tematu")
        self.assertEqual(email_db.sender, None, msg = u"Wysyłamy przez domyślny email")

    def test_send_mail_from_another_email(self):

        topic = u"Email_testowy"
        sender = Sender()
        sender.sender="sender@example.com"
        sender.auth_sender="sender@example.com"
        sender.password_sender = "test"
        sender.save()

        self.assertEqual(sender.get_plain_password(), u"test", msg=u"hasło powinno być dobrze odkodowane")

        send_email(self.request, topic, template="emails/emails/base_email.html", user = self.user, data_email = {}, is_send_now = False, sender= sender)

        email_db = Email.objects.get(id = 1)

        self.assertEqual(email_db.sender.id, sender.id , msg=u"Nadawca powinien być taki sam jak ten zdefiniowany")


    def test_emails_exceptions(self):
        topic = u"Email_testowy"
        #send_email(self.request, topic, template="emails/emails/base_email.html", user = self.user, email="test81@example.com", data_email = {}, is_send_now = False)
        self.assertRaises(Diffrent_emails, send_email, self.request, topic, template="emails/emails/base_email.html", user = self.user, email="test81@example.com", data_email = {}, is_send_now = False )
        self.assertRaises(Email_is_empty, send_email, self.request, topic, template="emails/emails/base_email.html", data_email = {}, is_send_now = False )

        #send_email(self.request, topic, template="emails/emails/base_email.html", data_email = {}, is_send_now = False)

class EmailSend_Management_Command(TestCase):
    """
        Klasa testująca polecenie send_mails wywoływane z konsoli
    """


class Send_EmailTestCase(TestCase):
    """
        Funkcja sprawdzająca  send_mail
    """

    def setUp(self):
        requestMock = RequestMock()
        self.request = requestMock.get_request_mock()
        self.user = User.objects.create_user("Test",email= "user@example.com", password = "test")

    def testSend_at(self):
        topic = u"Email_testowy"
        send_email(self.request, topic, template="emails/emails/base_email.html", data_email = {},
                   is_send_now = False, send_at=datetime.datetime.now() + relativedelta(seconds=2),
                    email="test@example.com" )

        self.assertEqual(Email.objects.filter(is_send=True).count(), 0, msg=u"Nic nie powinno zostać wysłane")
        self.assertEqual(Email.objects.filter(is_send=False).count(), 1, msg=u"Musi być jeden niewysłany mail")
        time.sleep(2)
        send_non_send_email()
        self.assertEqual(Email.objects.filter(is_send=True).count(), 1, msg=u"Coś powinno zostać wysłane")
        self.assertEqual(Email.objects.filter(is_send=False).count(), 0, msg=u"Nic nie powinno nie zostać wysłane")

    def testIs_send_now(self):
        topic = u"Email_testowy"
        send_email(self.request, topic, template="emails/emails/base_email.html", data_email = {},
                   is_send_now = False,
                    email="test@example.com" )
        self.assertEqual(Email.objects.filter(is_send=True).count(), 0, msg=u"Nic nie powinno zostać wysłane")
        self.assertEqual(Email.objects.filter(is_send=False).count(), 1, msg=u"Musi być jeden niewysłany mail")

        send_email(self.request, topic, template="emails/emails/base_email.html", data_email = {},
                   is_send_now = True,
                    email="test@example.com" )

        self.assertEqual(Email.objects.filter(is_send=True).count(), 1, msg=u"Coś powinno zostać wysłane")
        self.assertEqual(Email.objects.filter(is_send=False).count(), 1, msg=u"Musi być jeden niewysłany mail")


    def testShow_by_key(self):
        topic = u"Email_testowy"
        data_email = {}

        send_email(self.request, topic, template="emails/emails/base_email.html", user = self.user, data_email = {}, is_send_now = False)

        email_db = Email.objects.all()[0]

        response = self.client.get(reverse('emails:show', args=[email_db.key]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('emails:show', args=[email_db.key+'niematego']))
        self.assertEqual(response.status_code, 404)

    def testKey_unique(self):
        topic = u"Email_testowy"
        data_email = {}

        send_email(self.request, topic, template="emails/emails/base_email.html", user = self.user, data_email = {}, is_send_now = False)
        send_email(self.request, topic, template="emails/emails/base_email.html", user = self.user, data_email = {}, is_send_now = False)
        send_email(self.request, topic, template="emails/emails/base_email.html", user = self.user, data_email = {}, is_send_now = False)

        email = Email.objects.all().order_by('-id')[0]
        self.assertEqual(Email.objects.filter(key=email.key).count(), 1)
