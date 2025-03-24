import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

def print_status(message, is_success):
    """Красиво выводит статус операции"""
    color = "\033[92m" if is_success else "\033[91m"
    symbol = "✓" if is_success else "✗"
    print(f"{color}[{symbol}] {message}\033[0m")

def send_email(sender_email, sender_password, recipient_email, subject, message):
    try:
        # Создание сообщения
        print_status("Формирование письма...", True)
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        time.sleep(1)

        # Подключение к серверу
        print_status("Подключение к SMTP серверу Gmail...", True)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        time.sleep(1)

        # Авторизация
        print_status("Авторизация...", True)
        server.login(sender_email, sender_password)
        time.sleep(1)

        # Отправка
        print_status("Отправка письма...", True)
        server.send_message(msg)
        time.sleep(1)

        # Завершение
        print_status("Письмо успешно отправлено!", True)
        return True
    
    except smtplib.SMTPAuthenticationError:
        print_status("Ошибка авторизации: неверный логин/пароль", False)
    except smtplib.SMTPException as e:
        print_status(f"Ошибка SMTP: {str(e)}", False)
    except Exception as e:
        print_status(f"Неожиданная ошибка: {str(e)}", False)
    finally:
        if 'server' in locals():
            server.quit()
    return False

if __name__ == "__main__":
    print("\n=== 🚀 Gmail Отправитель ===")
    print("ℹ️ Для выхода нажмите Ctrl+C\n")
    
    try:
        # Ввод данных
        sender_email = input("Ваш Gmail: ").strip()
        sender_password = input("Пароль/App Password: ").strip()
        recipient_email = input("Получатель: ").strip()
        subject = input("Тема: ").strip()
        
        print("\nВведите текст письма (Ctrl+D для завершения):")
        message_lines = []
        while True:
            try:
                line = input()
                message_lines.append(line)
            except EOFError:
                break
        
        # Отправка
        print("\n⌛ Начинаем отправку...")
        success = send_email(
            sender_email,
            sender_password,
            recipient_email,
            subject,
            "\n".join(message_lines)
        )
        
        # Итоговый результат
        if success:
            print("\n🎉 Письмо успешно доставлено!")
        else:
            print("\n😞 Не удалось отправить письмо")
        
    except KeyboardInterrupt:
        print("\n⛔ Программа прервана пользователем")
