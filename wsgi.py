"""WSGI entry point for PythonAnywhere (and any other WSGI server).

On PythonAnywhere, replace the contents of the generated
/var/www/<username>_pythonanywhere_com_wsgi.py file with:

    import sys, os
    project = "/home/<username>/scholarship-portal"
    if project not in sys.path:
        sys.path.insert(0, project)
    os.environ.setdefault("SECRET_KEY", "<paste a long random string>")
    os.environ.setdefault("SESSION_COOKIE_SECURE", "1")
    from wsgi import application
"""
from app import create_app

application = create_app()
app = application
