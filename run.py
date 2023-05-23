from app import sdx_app, setup_keys, CONFIG
from app.collect import process

if __name__ == '__main__':
    setup_keys()
    sdx_app.add_pubsub_endpoint(process, CONFIG.QUARANTINE_TOPIC_ID)
    sdx_app.run(port=5000)
