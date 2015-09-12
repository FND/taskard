META = {
    "install_requires": ["Flask"],
    "extras_require": {
        "linting": ["pep8"]
    }
}


if __name__ == "__main__":
    setup(**META)
