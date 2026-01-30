import smtplib
import os
import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def get_user_config():
    config = {}
    print("--- Konfigurace odeslání e-mailu ---")
    config["SENDER_EMAIL"] = input("Zadejte Váš e-mail (odesílatel): ")
    print(f"Zadejte heslo pro aplikaci k e-mailu {config['SENDER_EMAIL']}:")
    config["SENDER_PASSWORD"] = getpass.getpass()
    config["RECEIVER_EMAIL"] = input("Zadejte e-mail auditora (příjemce): ")
    config["SMTP_SERVER"] = "smtp.gmail.com"
    config["SMTP_PORT"] = 587
    print("---------------------------------------")
    return config

def create_email_message(sender, receiver):
    subject = "Žádost o audit: AI Agenti (Fáze vývoje)"
    body = """
Vážený pane/paní senior auditore,

obracím se na Vás se žádostí o provedení technického a procesního auditu našeho projektu AI agentů.

Projekt se aktuálně nachází v aktivní fázi vývoje. Cílem tohoto auditu není finální hodnocení, ale spíše preventivní identifikace potenciálních rizik a získání doporučení pro zvýšení bezpečnosti, stability a efektivity systému před jeho nasazením do produkčního prostředí.

Žádáme o zaměření auditu na následující klíčové oblasti:
1.  Bezpečnostní analýza: Odolnost vůči Prompt Injection, zabezpečení nástrojů a API, ochrana dat.
2.  Logika a rozhodovací proces: Analýza chování v okrajových situacích, ověření spolehlivosti.
3.  Správa zdrojů a efektivita: Optimalizace nákladů, detekce zacyklení.
4.  Kvalita kódu a architektury: Posouzení udržitelnosti a škálovatelnosti.

Prosím o návrh možného termínu pro úvodní schůzku, kde bychom Vám představili architekturu projektu a upřesnili rozsah auditu.

S pozdravem,

OMEGA
(jednající z pověření operátora)
    """
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = Header(subject, 'utf-8')
    message.attach(MIMEText(body.replace("\n", "<br>"), 'html', 'utf-8'))
    return message.as_string()

def send_email(config, message):
    try:
        print(">>> Navazuji spojení s SMTP serverem...")
        server = smtplib.SMTP(config["SMTP_SERVER"], config["SMTP_PORT"])
        server.starttls()
        server.login(config["SENDER_EMAIL"], config["SENDER_PASSWORD"])
        print(">>> Odesílám žádost o audit...")
        server.sendmail(config["SENDER_EMAIL"], config["RECEIVER_EMAIL"], message)
        print(">>> Žádost o audit byla úspěšně odeslána.")
    except smtplib.SMTPAuthenticationError:
        print("[ERROR] Chyba autentizace. Zkontrolujte e-mail a heslo pro aplikace.")
    except Exception as e:
        print(f"[ERROR] Nepodařilo se odeslat e-mail: {e}")
    finally:
        if 'server' in locals() and server:
            server.quit()
            print(">>> Spojení s SMTP serverem ukončeno.")

if __name__ == "__main__":
    user_config = get_user_config()
    email_content = create_email_message(user_config["SENDER_EMAIL"], user_config["RECEIVER_EMAIL"])
    send_email(user_config, email_content)
