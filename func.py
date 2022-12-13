import yaml
from yaml.loader import SafeLoader
import requests
import json
import os
import logging


logging.basicConfig(level=logging.INFO)


def loadConfig() -> dict:
    """Loads config from config path

    Returns:
        dict: config dict of dicts
    """
    logging.debug('Loading config')
    CONFIG_PATHS = [
        './',
        '/etc/hachivsd/'
        '~/.config/hachivsd/'
    ]
    CONFIG_FILES = [
        '.config.yml',
        'config.yml',
        'config.yaml',
        'cfg.yml',
        'cfg.yaml',
        'hachivsd.yml',
        'hachivsd.yaml'
    ]
    for path in CONFIG_PATHS:
        for file in CONFIG_FILES:
            try:
                with open(f"{path}{file}", 'r') as f:
                    LOADED_CONFIG = yaml.load(f, Loader=SafeLoader)
                    logging.info(f"Config loaded from {path}{file}")
                    break
            except Exception:
                pass
    return LOADED_CONFIG


def getEngine(vault: dict) -> list:
    """Gets list of secrets in engine

    Args:
        vault (dict): 'vault' section of config e.g. config['vault']

    Returns:
        list: list of secret names
    """
    logging.debug('Requesting secrets list')
    headers = {
        'X-Vault-Token': vault['token']
    }
    url = f"{vault['url']}/v1/{vault['engine']}/metadata"
    r = requests.request(method='LIST', url=url, headers=headers)
    secrets = r.json()
    return secrets['data']['keys']


def getSecrets(vault: dict, secrets: list) -> dict:
    """Iterates secrets list and gets data from vault

    Args:
        vault (dict): 'vault' section of config, e.g. config['vault']
        secrets (list): list of secrets names

    Returns:
        dict: secrets data
    """
    logging.info('Getting secrets contents')
    headers = {
        'X-Vault-Token': vault['token']
    }
    url = f"{vault['url']}/v1/{vault['engine']}/data"
    data = {}
    for i, s in enumerate(secrets):
        r = requests.request(method='GET', url=f"{url}/{s}", headers=headers)
        secret = r.json()['data']['data']
        data[s] = secret
        logging.debug(f"Got {i+1} of {len(secrets)} secrets")
    return data


def formatAs(secret: dict, kind: str = 'env') -> str:
    """Formats secret with defined type

    Args:
        secret (dict): secret data
        kind (str, optional): Type of formatting (json/yml/yaml/env). \
            Defaults to 'env'.
        json is JSON
        yml, yaml is YAML
        env is key: value format

    Returns:
        str: formatted multiline string
    """
    output = ''
    for p in ['__filename__', '__path__', '__type__']:
        secret.pop(p, None)
    match kind:
        case 'json':
            output = json.dumps(secret, indent=4)
        case 'yml' | 'yaml':
            output = yaml.dump(secret, indent=4)
        case _:
            for k, v in secret.items():
                output += f"{k}={v}\n"
    logging.debug(f"Formatted output as {kind}")
    return output


def saveSecret(secret: dict, secret_name: str, config: dict):
    """Save secret with formatting, respecting config

    Args:
        secret (dict): secret data
        secret_name (str): name of secret from secrets list
        config (dict): 'output' section of config, e.g. config['output']
    """
    try:
        path = secret['__path__']
    except Exception:
        pass
    try:
        path = config['path-override']
        logging.debug(f"Path overriden by local config to {path}")
    except Exception:
        path = ''

    try:
        mode = secret['__type__']
    except Exception:
        pass
    try:
        mode = config['mode-override']
        logging.debug(f"Output file overriden by local config to {mode}")
    except Exception:
        mode = 'none'

    try:
        base = config['basepath']
    except ValueError:
        logging.error('Error: Mandatory option output:basepath \
            not defined in config.')

    try:
        filename = secret['__filename__']
    except Exception:
        filename = secret_name

    try:
        prefix = config['name-prefix']
    except Exception:
        prefix = ''
    try:
        suffix = config['name-suffix']
    except Exception:
        suffix = ''

    fullpath = f"{base}/{path}".replace('//', '/')
    filename = f"{prefix}{filename}{suffix}"

    try:
        os.makedirs(fullpath, exist_ok=True)
    except NotADirectoryError:
        logging.error('Unable to create a directory to save files')
        exit()
    try:
        with open(f"{fullpath}/{filename}".replace('//', '/'), 'w+') as f:
            f.write(formatAs(secret, kind=mode))
        logging.info(f"{fullpath}/{filename}".replace('//', '/') + ' saved')
    except OSError:
        logging.error('Error: Unable to save secret to file')
