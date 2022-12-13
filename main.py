import func
import logging


logging.basicConfig(level=logging.INFO)

try:
    config = func.loadConfig()
    logging.info('Config loaded successfully')
except Exception:
    logging.error('Error: Unable to get config')
    exit()

try:
    engine = func.getEngine(config['vault'])
    logging.info('Secrets list retrieved')
except ConnectionError:
    logging.error('Error: Unable to retrieve secrets list from vault')
    exit()

try:
    secrets = func.getSecrets(config['vault'], engine)
    logging.info('Secrets data retrieved')
except ConnectionError:
    logging.error('Error: Unable to retrieve secrets content')
    exit()

try:
    logging.info(f"Saving {len(secrets)} secrets")
    for k, v in secrets.items():
        func.saveSecret(secret=v, secret_name=k, config=config['output'])
    logging.info('Secrets saved')
except OSError:
    logging.error('Error Unable to save secrets')
    exit()
