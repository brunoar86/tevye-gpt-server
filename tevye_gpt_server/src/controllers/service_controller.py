import structlog

from fastapi import HTTPException, status

from tevye_gpt_server.src.utils.service_registry import SERVICE_REGISTRY

log = structlog.get_logger(__name__='service controller')


class ServiceRequest():

    def __init__(self):
        self.service = None
        self.payload = {}

    async def request(self, data):
        self.service = data.service
        self.payload = data.payload

        response = await self.process_request()
        return response

    async def process_request(self):
        log.info(f"Processing request for {self.service}...")
        service_handler = SERVICE_REGISTRY.get(self.service)

        if not service_handler:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Service not found")

        result = await service_handler.request(self.payload)
        log.info(f"Service {self.service} processed successfully.")
        return result


service = ServiceRequest()
