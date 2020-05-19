from django.conf import settings
import sendgrid
import base64
from tempfile import TemporaryDirectory
import os
from sendgrid.helpers import mail

class Mail:
    def __init__(self, to=[], subject='', message='', cc=[]):
        self._from = mail.From("expertcovers2020@gmail.com", "Expert Traders")
        self.replyto = mail.ReplyTo('expertcovers2020@gmail.com', 'Expert Traders')
        self.to = [mail.To(i[0],i[1]) for i in to]
        if cc:
            self.cc = [mail.Cc(i[0], i[1]) for i in cc]
        else:
            self.cc = None
        self.subject = mail.Subject(subject)
        self.content = mail.Content(mail.MimeType.text, message)
        self.attachment = None

    def add_attachment(self, f):
        tmp_dir = TemporaryDirectory()
        path = os.path.join(tmp_dir.name, 'challan_report.pdf')
        with open(path, 'wb+') as des:
            for chunk in f.chunks():
                des.write(chunk)
        with open(path, 'rb') as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        a = mail.Attachment()
        a.file_content = mail.FileContent(encoded)
        a.file_type = mail.FileType('application/pdf')
        a.file_name = mail.FileName('challan_report.pdf')
        a.disposition = mail.Disposition('attachment')
        a.content_id = mail.ContentId('Example Content ID')
        self.attachment = a


    def send(self):
        m = mail.Mail()
        m.to = self.to
        m.from_email = self._from
        m.reply_to = self.replyto
        if self.cc:
            m.cc = self.cc
        m.subject = self.subject
        m.content = self.content
        if self.attachment:
            m.attachment = self.attachment
        s = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        response = s.send(m)