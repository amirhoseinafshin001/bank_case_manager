import webbrowser
import threading
from routes import create_app


app = create_app()


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


if __name__ == "__main__":
    threading.Timer(0.5, open_browser).start()
    # app.run(debug=True, use_reloader=False)
    app.run(use_reloader=False)
