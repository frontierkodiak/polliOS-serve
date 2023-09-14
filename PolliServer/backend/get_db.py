# PolliServer/backend/get_db.py
from PolliServer.backend.ServerBackendSingleton import ServerBackendSingleton


# Async dependency to get the database session
async def get_db():
    backend = ServerBackendSingleton()
    async with backend.session() as session:
        yield session