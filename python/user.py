
def get_config_dir(app_name=''):
    if "XDG_CONFIG_HOME" in os.environ:
        confighome = os.environ['XDG_CONFIG_HOME']
    elif "APPDATA" in os.environ:  # On Windows
        confighome = os.environ['APPDATA']
    else:
        try:
            from xdg import BaseDirectory
            confighome = BaseDirectory.xdg_config_home
        except ImportError:  # Most likely a Linux/Unix system anyway
            confighome = os.path.join(get_home_dir(), ".config")
    configdir = os.path.join(confighome, app_name)
    return configdir


def get_home_dir():
    if sys.platform == "cygwin":
        home_dir = os.getenv('HOME')
    else:
        home_dir = os.getenv('USERPROFILE') or os.getenv('HOME')
    if home_dir is not None:
        return os.path.normpath(home_dir)
    else:
        raise KeyError("Neither USERPROFILE or HOME environment variables set.")

