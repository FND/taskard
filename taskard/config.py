import os

import yaml


def configure_application(app):
    """
    loads configuration values from instance directory's `config.yaml`
    """
    with open(os.path.join(app.instance_path, "config.yaml")) as fh:
        config = yaml.safe_load(fh)

    app.config_mode = os.environ["TASKARD_ENV"]
    for key, value in config[app.config_mode].items():
        # fix relative paths to target instance directory -- XXX: special-casing
        if (key == "SQLALCHEMY_DATABASE_URI" and
                value.startswith("sqlite:///") and
                not value.startswith("sqlite:////")):
            filepath = value[10:]
            value = "sqlite:///" + os.path.join(app.instance_path, filepath)

        app.config[key] = value
