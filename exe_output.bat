pyinstaller --onefile --name=CaseManagerApp --add-data "templates;templates" --add-data "icon.png;." --hidden-import=sqlalchemy --hidden-import=jinja2 --hidden-import=werkzeug --hidden-import=jalali_core --hidden-import=jdatetime --icon=icon.png app.py