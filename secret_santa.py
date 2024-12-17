import json
import logging
import smtplib

from dataclasses import dataclass
from jinja2 import Template

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


@dataclass
class EmailConfig:
    """Email server configuration."""
    smtp_server: str
    port: int
    username: str
    password: str

@dataclass
class SecretSantaParticipant:
    """Represents a secret santa participant."""
    name: str
    email: str
    recipient_name: str = None

class EmailTemplate:
    """Handles email template rendering with a festive German template."""
    DEFAULT_TEMPLATE = """
    🎄 Wichtel-Alarm für {{ sender_name }}! 🎄

    Ho ho hooo! 

    Die Wichtel-Lotterie hat entschieden und Du hast das große Los gezogen:
    
    🎁 Trommelwirbel... Du bist der geheime Wichtel für...
    
    *~*~*~* {{ recipient_name }} *~*~*~*

    Ein paar wichtige Wichtel-Regeln:
    🤫 Pssst! Absolutes Stillschweigen ist Wichtel-Ehrensache!
    🎨 Sei kreativ - die besten Geschenke kommen von Herzen
    🌟 Mach's mysteriös - lass Dir was Besonderes einfallen
    
    Budget: 20 - 30 Euro
    
    Viel Spaß beim heimlichen Planen und Basteln! 🎅
    
    Fröhliche Wichtel-Grüße,
    Dein Christkind-Bot 🎄✨
    
    P.S.: Falls Du Fragen hast, antworte einfach nicht auf diese Mail - 
    der Wichtel-Bot kann leider keine Antworten lesen 🤖
    """
    def __init__(self, template_path: str = None):
        if template_path:
            try:
                with open(template_path, 'r') as f:
                    self.template = Template(f.read())
            except FileNotFoundError:
                logging.warning(f"Template file {template_path} not found, using default template")
                self.template = Template(self.DEFAULT_TEMPLATE)
        else:
            self.template = Template(self.DEFAULT_TEMPLATE)

    def render(self, sender_name: str, recipient_name: str) -> str:
        """Render the email template with given names."""
        return self.template.render(
            sender_name=sender_name,
            recipient_name=recipient_name
        )

class SecretSantaEmailer:
    """Handles the secret santa email sending process."""
    
    def __init__(self, email_config: EmailConfig, template: EmailTemplate = None):
        self.config = email_config
        self.template = template or EmailTemplate()
        self.logger = logging.getLogger(__name__)

    def _create_email_message(self, to_email: str, sender_name: str, recipient_name: str) -> MIMEMultipart:
        """Create email message with secret santa assignment."""
        message = MIMEMultipart()
        message["From"] = self.config.username
        message["To"] = to_email
        message["Subject"] = "Deine Wichtel-Aufgabe! 🎄"

        body = self.template.render(sender_name=sender_name, recipient_name=recipient_name)
        message.attach(MIMEText(body, "plain"))
        
        return message

    def send_mails(
            self, 
            matches: dict[str, str], 
            email_mapping: list[dict[str, str]]
        ) -> None:
        """Send secret santa assignment emails to all participants."""
        # Convert email mapping list to dictionary for easier lookup
        email_dict = {k: v for d in email_mapping for k, v in d.items()}
        
        try:
            with smtplib.SMTP(self.config.smtp_server, self.config.port) as server:
                server.starttls()
                server.login(self.config.username, self.config.password)
                
                for sender_name, recipient_name in matches.items():
                    try:
                        sender_email = email_dict.get(sender_name)
                        if not sender_email:
                            self.logger.error(f"No email found for {sender_name}")
                            continue

                        message = self._create_email_message(
                            sender_email,
                            sender_name,
                            recipient_name
                        )
                        
                        server.send_message(message)
                        self.logger.info(f"Successfully sent assignment email to {sender_name}")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to send email to {sender_name}: {str(e)}")
                        
        except Exception as e:
            self.logger.error(f"Failed to connect to email server: {str(e)}")
            raise

# Example usage:
if __name__ == "__main__":
    # Load configuration
    config = EmailConfig(
        smtp_server="smtp.gmail.com",
        port=587,
        username="marcelbraasch@gmail.com",
        password="ysslkrhsmccoxdmo"
    )
    
    # Sample data
    # matches = {
    #     "Name1": "Name2",
    #     "Name2": "Name3",
    #     "Name3": "Name1"
    # }
    
    # email_mapping = [
    #     {"Name1": "marcelbraasch@gmail.com"},
    #     {"Name2": "marcelbraasch@gmail.com"},
    #     {"Name3": "marcelbraasch@gmail.com"},
    # ]

    # Sample data
    matches_path = "matches.json"
    with open(matches_path, "r") as f:
        matches = json.load(f)

    # Email mapping
    email_mapping_path = "email_mapping.json"
    with open(email_mapping_path, "r") as f:
        unformatted = json.load(f)
        # flatten the list of dictionaries
        email_mapping = [{k: v} for d in unformatted for k, v in d.items()]


    # Initialize and send emails
    emailer = SecretSantaEmailer(config)
    emailer.send_mails(matches, email_mapping)