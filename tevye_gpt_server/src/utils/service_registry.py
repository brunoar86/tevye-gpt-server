from tevye_gpt_server.src.modules.services import (
    ServiceHandler, ChatCompletion
    )

SERVICE_REGISTRY: dict[str, ServiceHandler] = {
    'chat_completion': ChatCompletion()
}
