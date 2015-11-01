from taskard import __version__ as VERSION


META = {
    "name": "taskard",
    "version": VERSION,
    "url": "https://github.com/FND/taskard",
    "author": "FND",
    "install_requires": ["Flask", "Flask-SQLAlchemy"],
    "extras_require": {
        "development": ["colorama"],
        "testing": ["gabbi", "gabbi-html", "pytest"],
        "linting": ["pep8"]
    }
}


if __name__ == "__main__":
    from setuptools import setup
    setup(**META)
