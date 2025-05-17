import smtplib
from common import fread
from config import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from logging import getLogger

class SMTP:

    def __init__(self) -> None:
        self.logger = getLogger(__name__)
        self.hosts = self.get_event_hostlist()
        if not self.hosts:
            raise ValueError("No hosts found. Please check your configuration.")


    def get_event_hostlist(self) -> list:
        return [eh for eh in config['hostlist'] if eh and not str(eh).startswith(('#', '\n'))]


    def build_multipart_msg(self, subj_title: str, payload: str) -> MIMEMultipart: 
        message = MIMEMultipart()
        message['From'] = Header(config['smtp']['sender'], config['encoding'])
        message['To'] = Header(', '.join(config['smtp']['recipients']).strip(), config['encoding'])
        message['Subject'] = Header(subj_title, config['encoding'])
        message.attach(MIMEText(payload, config['smtp']['mime_type'], config['encoding']))
        return message


    def notify_email(self) -> int:
        if len(self.hosts) < 1:
            self.logger.error(f"Error: No event hosts found in list: {config['hostlist']}")
            return 1

        payload = '\n{}\n'.format(fread(config['logger']['log_file'], encoding=config['encoding']))
        subj_title = 'Latest events fetched: {}'.format(config['logger']['log_ts'])
        contents = 'Subject: {}\n\n{}'.format(subj_title, payload)

        try:
            with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
                server.starttls()

                if config['smtp'].get('sender') and config['smtp'].get('app_passkey'):
                    server.login(config['smtp']['sender'], config['smtp']['app_passkey'])
                    self.logger.debug('Successfuly logged in to SMTP server.')
                else:
                    self.logger.debug('Not using SMTP authentication.')

                server.sendmail(
                    config['smtp']['sender'], 
                    config['smtp']['recipients'], 
                    self.build_multipart_msg(subj_title, contents).as_string()
                )
                self.logger.info(f"Notification sent to {len(config['smtp']['recipients'])} recipients.")

        except smtplib.SMTPException as e:
            self.logger.error(f"{e.__class__.__name__} exception raised: {e.args[::-1]}")
            return 1 
        except Exception as e:
            self.logger.error(f"Unknown SMTP exception raised: {e.args[::-1]}")
            return 1 
        
        return 0
