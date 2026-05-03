import httpx
import logging

class BaseAdapter:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def sync_data(self, data: dict):
        raise NotImplementedError("Each department must implement sync_data")

class FactoriesAdapter(BaseAdapter):
    async def sync_data(self, data: dict):
        # Implementation to call Factories Legacy API
        async with httpx.AsyncClient() as client:
            # response = await client.post(f"{self.base_url}/update", json=data)
            logging.info(f"Syncing to Factories: {data}")
            return {"status": "success"}

class LabourAdapter(BaseAdapter):
    async def sync_data(self, data: dict):
        # Implementation to call Labour Legacy API
        logging.info(f"Syncing to Labour: {data}")
        return {"status": "success"}
