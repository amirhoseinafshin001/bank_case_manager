import webbrowser
import threading
import socket
from tkinter import messagebox
from tkinter import Tk

from routes import create_app



app = create_app()


def find_free_port(start_port=9561, max_attempts=20):
    """پیدا کردن یک پورت آزاد از start_port به بعد."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:  # پورت اشغال است
            continue
    raise Exception(f"هیچ پورت آزادی در محدوده {start_port}-{start_port + max_attempts} یافت نشد!")


def open_browser(port):
    webbrowser.open_new(f'http://127.0.0.1:{port}/')


if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    try:
        selected_port = find_free_port()
    except Exception as e:
        messagebox.showerror(
            title="خطا در اجرای برنامه",
            message=str(e)
        )

    print(f"http://127.0.0.1:{selected_port}")    
    threading.Timer(0.5, lambda: open_browser(selected_port)).start()
    app.run(port=selected_port, use_reloader=False)
