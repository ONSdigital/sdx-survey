from pathlib import Path

from sdx_base.run import run
from sdx_base.server.server import RouterConfig
from sdx_base.server.tx_id import txid_from_pubsub

from app.routes import router, unrecoverable_error_handler
from app.settings import Settings

if __name__ == '__main__':
    proj_root = Path(__file__).parent  # sdx-survey dir
    router_config = RouterConfig(router,
                                 tx_id_getter=txid_from_pubsub,
                                 on_unrecoverable_handler=unrecoverable_error_handler)
    run(Settings, routers=[router_config], proj_root=proj_root)
