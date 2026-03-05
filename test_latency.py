"""Test latency data retrieval"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.services.monitoring_service import MonitoringService
from sqlalchemy import select
from app.models.api import ApiEndpoint

async def test_latency():
    async with AsyncSessionLocal() as db:
        # First get an endpoint
        result = await db.execute(select(ApiEndpoint).limit(1))
        endpoint = result.scalar_one_or_none()
        
        if not endpoint:
            print("No endpoints found!")
            return
        
        print(f"Testing endpoint: {endpoint.id} - {endpoint.name}")
        
        service = MonitoringService(db)
        result = await service.get_response_time_series(api_endpoint_id=endpoint.id, hours=24)
        print('Result type:', type(result))
        print('Result data:', result.data if hasattr(result, 'data') else result)
        
        # Also try to get logs directly
        from app.models.monitoring_log import MonitoringLog
        logs_result = await db.execute(
            select(MonitoringLog)
            .where(MonitoringLog.api_endpoint_id == endpoint.id)
            .order_by(MonitoringLog.checked_at.desc())
            .limit(5)
        )
        logs = logs_result.scalars().all()
        print(f"\nFound {len(logs)} logs for endpoint {endpoint.id}")
        for log in logs:
            print(f"  - {log.checked_at}: status={log.status}, response_time={log.response_time}ms")

if __name__ == "__main__":
    asyncio.run(test_latency())

