META = {
    "install_requires": ["Flask", "SQLAlchemy"],
    "extras_require": {
        "linting": ["pep8"]
    }
}


if __name__ == "__main__":
    setup(**META)
