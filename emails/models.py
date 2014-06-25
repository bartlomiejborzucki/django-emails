#-*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
#from Crypto.Cipher import AES
import base64
from django.http import Http404
from django.utils.encoding import smart_unicode

class Sender(models.Model):
    """
        Tabela do przechowuwania adresów email wraz z hasłami
    """
    sender = models.EmailField(default=False, null=True, blank=True)
    auth_sender = models.CharField(null=True, blank=True, max_length=40)
    password_sender = models.CharField(null=True, blank=True, max_length=1000)

    def __init__(self, *args, **kwargs):
        from Crypto.Cipher import AES
        self.key = '0123456789abcdef11DSADAR11FASRT1'
        self.mode = AES.MODE_CBC
        self.encryptor = AES.new(self.key, self.mode)
        self.decryptor = AES.new(self.key, self.mode)
        super(Sender, self).__init__(*args, **kwargs)


    def _len_multiple_16(self, input):
        """
            TODO: Funkcje można poprawić bo jest nieoptymalnie napisana
        """
        tmp_len = len(input)
        add_zero = 256 - 1 - tmp_len
        input = "#" + input
        while add_zero != 0:
            input = "0" + input
            add_zero -= 1
        return input



    def change_password(self):
        pass

    def get_plain_password(self):
        password = base64.b64decode(self.password_sender)
        plain = self.decryptor.decrypt(password)
        plain = plain.split("#")

        return ','.join(plain[1:])

    def create_password(self, password):

        return self.encryptor.encrypt(password)


    def save(self):

        if not self.id:
            self.password_sender = base64.b64encode(self.create_password(self._len_multiple_16(self.password_sender)))
        super(Sender, self).save()




class Email(models.Model):
    """ Tabela przechowywująca maile """
    topic = models.CharField(max_length=100)
    body = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="email_from_user", null=True)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, db_column='this_creation_date')
    send_at = models.DateTimeField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_send_by_S3 = models.BooleanField(default=False)
    is_send = models.BooleanField(default=True)
    #when it is null, we will send by default email
    sender = models.ForeignKey(Sender, null=True)

    key = models.CharField(db_index=True, max_length=60, default="0000000000000000000000000000000000000000")
    original_key = models.CharField(db_index=True, max_length=60, default="0000000000000000000000000000000000000000")

    class Meta:
        ordering = ['id']

    def __init__(self, *args, **kwargs):
        super(Email, self).__init__(*args, **kwargs)
        if not self.key or self.key == '0000000000000000000000000000000000000000':
            self.generate_key()

    def __unicode__(self):
        return unicode(u'Title: ') + unicode(self.topic) + smart_unicode(' to: ') + unicode(self.user)

    def get_absolute_url(self):
        return reverse('emails:show', args=[self.key])

    def generate_key(self):
        import hashlib
        key = "ADFGUEDSE12345#$!#%^@^#&BFmifdsjfiskdoakdposkanfsruehunvushfu,./;[]"

        if self.user:
            email = self.user.username.encode("utf8")
        else:
            email = self.email.encode("utf8")

        new_key = hashlib.sha224(key + self.topic.encode("utf8") + email).hexdigest()
        collision = Email.objects.filter(original_key=new_key).count()
        self.original_key = new_key
        if collision:
            new_key += str(collision)

        self.key = new_key


    @staticmethod
    def get_by_key(key):
        try:
            return Email.objects.get(key=key)
        except ObjectDoesNotExist:
            raise Http404
