META = {
    "install_requires": ["Flask", "Flask-SQLAlchemy"],
    "extras_require": {
        "testing": ["pytest"],
        "linting": ["pep8"]
    }
}


if __name__ == "__main__":
    setup(**META)
