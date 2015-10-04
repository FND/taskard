import os

import yaml


def configure_application(app):
    """
    loads configuration values from instance directory's `config.yaml`
    """
    try:
        with open(os.path.join(app.instance_path, "config.yaml")) as fh:
            config = yaml.safe_load(fh)
    except FileNotFoundError:
        raise ConfigurationError("missing configuration file")

    try:
        app.config_mode = os.environ["TASKARD_CONFIG"]
    except KeyError:
        raise ConfigurationError("configuration mode not set")
    try:
        settings = config[app.config_mode]
    except TypeError:
        raise ConfigurationError("missing configuration for mode '%s'" % app.config_mode)

    for key, value in settings.items():
        # fix relative paths to target instance directory -- XXX: special-casing
        if (key == "SQLALCHEMY_DATABASE_URI" and
                value.startswith("sqlite:///") and
                not value.startswith("sqlite:////")):
            filepath = value[10:]
            value = "sqlite:///" + os.path.join(app.instance_path, filepath)

        app.config[key] = value


class ConfigurationError(Exception):
    pass
