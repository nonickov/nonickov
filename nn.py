import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, sender_password, recipient_email, subject, message):
    try:
        # Создаем сообщение
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        # Отправляем через SMTP Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("\n✅ Письмо успешно отправлено!")
    
    except Exception as e:
        print(f"\n❌ Ошибка: {str(e)}")

if __name__ == "__main__":
    print("=== Отправка письма через Gmail ===")
    
    # Ввод данных
    sender_email = input("Ваш Gmail: ").strip()
    sender_password = input("Пароль (или App Password): ").strip()
    recipient_email = input("Кому (email): ").strip()
    subject = input("Тема: ").strip()
    print("Текст письма (Ctrl+Z + Enter для завершения):")
    
    # Многострочный ввод текста
    message = []
    while True:
        try:
            line = input()
            message.append(line)
        except EOFError:
            break
    
    # Отправка
    send_email(
        sender_email,
        sender_password,
        recipient_email,
        subject,
        "\n".join(message)
  )
