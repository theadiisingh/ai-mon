"""
Frontend-Backend Integration Tests
Verifies that frontend API calls match backend endpoints.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient


class TestFrontendBackendIntegration:
    """
    Integration tests to verify frontend-backend API synchronization.
    """
    
    @pytest.mark.asyncio
    async def test_auth_login_endpoint_format(self, client: AsyncClient, test_user):
        """
        Test that login works with form data (OAuth2 format).
        Frontend must send form data, not JSON.
        """
        response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_users_me_endpoint(self, client: AsyncClient, test_user):
        """
        Test /users/me endpoint for getting current user.
        """
        login_response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        
        response = await client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
    
    @pytest.mark.asyncio
    async def test_monitoring_logs_endpoint(self, client: AsyncClient, test_user, test_api_endpoint):
        """
        Test /monitoring/logs endpoint.
        """
        login_response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        
        response = await client.get(
            "/api/monitoring/logs",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    @pytest.mark.asyncio
    async def test_metrics_overview_endpoint(self, client: AsyncClient, test_user, test_api_endpoint):
        """
        Test /metrics/overview endpoint.
        """
        login_response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        
        response = await client.get(
            "/api/metrics/overview",
            headers={"Authorization": f"Bearer {token}"},
            params={"api_endpoint_id": test_api_endpoint.id, "hours": 24}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_metrics_uptime_endpoint(self, client: AsyncClient, test_user, test_api_endpoint):
        """
        Test /metrics/uptime endpoint.
        """
        login_response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        
        response = await client.get(
            "/api/metrics/uptime",
            headers={"Authorization": f"Bearer {token}"},
            params={"api_endpoint_id": test_api_endpoint.id, "days": 7}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_metrics_response_time_endpoint(self, client: AsyncClient, test_user, test_api_endpoint):
        """
        Test /metrics/response-time endpoint.
        """
        login_response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        
        response = await client.get(
            "/api/metrics/response-time",
            headers={"Authorization": f"Bearer {token}"},
            params={"api_endpoint_id": test_api_endpoint.id, "hours": 24}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_api_endpoints_crud(self, client: AsyncClient, test_user):
        """
        Test API endpoints CRUD operations.
        """
        login_response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        
        create_response = await client.post(
            "/api/apis/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Integration Test API",
                "url": "https://httpbin.org/status/200",
                "method": "GET",
                "expected_status_code": 200,
                "timeout_seconds": 30,
                "interval_seconds": 60
            }
        )
        assert create_response.status_code == 201
        endpoint_id = create_response.json()["id"]
        
        list_response = await client.get(
            "/api/apis/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert list_response.status_code == 200
        
        get_response = await client.get(
            f"/api/apis/{endpoint_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 200
        
        update_response = await client.put(
            f"/api/apis/{endpoint_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Updated Test API"}
        )
        assert update_response.status_code == 200
        
        delete_response = await client.delete(
            f"/api/apis/{endpoint_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert delete_response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_monitoring_analyze_endpoint(self, client: AsyncClient, test_user, test_api_endpoint):
        """
        Test /monitoring/analyze endpoint for AI analysis.
        Backend expects: api_endpoint_id, time_range_hours, log_ids, analysis_type
        """
        login_response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        
        response = await client.post(
            "/api/monitoring/analyze",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "api_endpoint_id": test_api_endpoint.id,
                "time_range_hours": 24
            }
        )
        
        assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_monitoring_health_check_status(self, client: AsyncClient, test_user):
        """
        Test /metrics/health-check/status endpoint.
        """
        login_response = await client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]
        
        response = await client.get(
            "/api/metrics/health-check/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200


class TestAPIEndpointMapping:
    """
    Documents the correct frontend-backend endpoint mapping.
    """
    
    # AUTH ENDPOINTS (backend: /api/auth/*)
    # - POST /api/auth/register - works with JSON
    # - POST /api/auth/login - MUST use form data (OAuth2PasswordRequestForm)
    # - POST /api/auth/refresh - needs Bearer token
    
    # USER ENDPOINTS (backend: /api/users/*)
    # - GET /api/users/me - Get current user (NOT /api/auth/me)
    
    # API ENDPOINTS (backend: /api/apis/*)
    # - GET /api/apis/ - List endpoints
    # - POST /api/apis/ - Create endpoint
    # - GET /api/apis/{id} - Get endpoint
    # - PUT /api/apis/{id} - Update endpoint
    # - DELETE /api/apis/{id} - Delete endpoint
    # - POST /api/apis/{id}/toggle - Toggle status
    # - POST /api/apis/{id}/pause - Pause monitoring
    # - POST /api/apis/{id}/resume - Resume monitoring
    
    # MONITORING ENDPOINTS (backend: /api/monitoring/*)
    # - GET /api/monitoring/logs - Get logs
    # - GET /api/monitoring/logs/{id} - Get single log
    # - GET /api/monitoring/endpoints/{id}/anomalies - Get anomalies
    # - GET /api/monitoring/endpoints/{id}/baseline - Get baseline
    # - POST /api/monitoring/analyze - Trigger AI analysis
    
    # METRICS ENDPOINTS (backend: /api/metrics/*)
    # - GET /api/metrics/overview - Get metrics overview
    # - GET /api/metrics/uptime - Get uptime metrics
    # - GET /api/metrics/response-time - Get response time series
    # - GET /api/metrics/status-codes - Get status code distribution
    # - GET /api/metrics/error-rate - Get error rate
    # - GET /api/metrics/health-check/status - Get monitoring status
    
    pass
