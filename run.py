from app import sdx_app, setup_keys, CONFIG
from app.collect import process, get_tx_id_from_object_id

if __name__ == '__main__':
    setup_keys()
    sdx_app.add_pubsub_endpoint(
        process,
        tx_id_getter=get_tx_id_from_object_id,
        quarantine_topic_id=CONFIG.QUARANTINE_TOPIC_ID)

    sdx_app.run(port=5000)
