import func
import logging


logging.basicConfig(level=logging.INFO)

try:
    config = func.loadConfig()
    logging.debug('Config loaded successfully')
except Exception:
    logging.error('Error: Unable to get config')

try:
    engine = func.getEngine(config['vault'])
    logging.debug('Secrets list retrieved')
except ConnectionError:
    logging.error('Error: Unable to retrieve secrets list from vault')

try:
    secrets = func.getSecrets(config['vault'], engine)
    logging.debug('Secrets data retrieved')
except ConnectionError:
    logging.error('Error: Unable to retrieve secrets content')

try:
    logging.info(f"Saving {len(secrets)} secrets")
    for k, v in secrets.items():
        func.saveSecret(secret=v, secret_name=k, config=config['output'])
    logging.debug('Secrets saved')
except OSError:
    logging.error('Error Unable to save secrets')
