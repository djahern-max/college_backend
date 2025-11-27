"""
Tests for system and health endpoints.
Fixed to handle plain text response from /routes-simple.
"""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for GET /"""

    def test_root_endpoint_success(self, client: TestClient):
        """Test root endpoint returns success."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "status" in data or "name" in data

    def test_root_endpoint_contains_app_info(self, client: TestClient):
        """Test root endpoint contains application information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        # Should contain some identifying information
        assert isinstance(data, dict)
        # Common patterns in root endpoints
        possible_keys = ["message", "name", "version", "status", "api", "service"]
        assert any(key in data for key in possible_keys)

    def test_root_endpoint_no_auth_required(self, client: TestClient):
        """Test that root endpoint is publicly accessible."""
        response = client.get("/")

        assert response.status_code == 200
        # Should work without authentication

    def test_root_endpoint_json_response(self, client: TestClient):
        """Test that root endpoint returns JSON."""
        response = client.get("/")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")


class TestHealthEndpoint:
    """Tests for GET /health"""

    def test_health_check_success(self, client: TestClient):
        """Test health check returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["ok", "healthy", "up", "running"]

    def test_health_check_structure(self, client: TestClient):
        """Test health check response structure."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

        # Common health check fields
        expected_fields = ["status"]
        for field in expected_fields:
            assert field in data

    def test_health_check_database_connection(self, client: TestClient):
        """Test that health check verifies database connection."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # If database status is included, it should be healthy
        if "database" in data:
            assert data["database"] in ["ok", "healthy", "connected"]

    def test_health_check_no_auth_required(self, client: TestClient):
        """Test that health check is publicly accessible."""
        response = client.get("/health")

        assert response.status_code == 200
        # Should work without authentication

    def test_health_check_json_response(self, client: TestClient):
        """Test that health check returns JSON."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")

    def test_health_check_performance(self, client: TestClient):
        """Test that health check responds quickly."""
        import time

        start_time = time.time()
        response = client.get("/health")
        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        # Health check should respond in less than 1 second
        assert elapsed_time < 1.0

    def test_health_check_includes_timestamp(self, client: TestClient):
        """Test that health check may include timestamp."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Timestamp is optional but common
        if "timestamp" in data or "time" in data:
            assert isinstance(data.get("timestamp") or data.get("time"), str)


class TestRoutesSimpleEndpoint:
    """Tests for GET /routes-simple"""

    def test_routes_simple_success(self, client: TestClient):
        """Test routes-simple endpoint returns route list."""
        response = client.get("/routes-simple")

        assert response.status_code == 200
        # This endpoint returns plain text, not JSON
        assert response.headers["content-type"].startswith("text/plain")
        data = response.text
        assert len(data) > 0

    def test_routes_simple_contains_routes(self, client: TestClient):
        """Test that routes-simple contains actual routes."""
        response = client.get("/routes-simple")

        assert response.status_code == 200
        data = response.text.lower()

        # Should contain some known routes
        assert any(
            endpoint in data
            for endpoint in ["institutions", "scholarships", "auth", "profiles", "api"]
        )

    def test_routes_simple_includes_methods(self, client: TestClient):
        """Test that routes include HTTP methods."""
        response = client.get("/routes-simple")

        assert response.status_code == 200
        data = response.text.upper()

        # Should contain HTTP methods
        assert any(
            method in data for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]
        )

    def test_routes_simple_includes_auth_routes(self, client: TestClient):
        """Test that routes include authentication endpoints."""
        response = client.get("/routes-simple")

        assert response.status_code == 200
        data = response.text.lower()

        # Should include auth-related routes
        assert "auth" in data or "login" in data or "register" in data

    def test_routes_simple_includes_api_version(self, client: TestClient):
        """Test that routes include API version path."""
        response = client.get("/routes-simple")

        assert response.status_code == 200
        data = response.text.lower()

        # Should include v1 API routes
        assert "v1" in data or "/api" in data

    def test_routes_simple_no_auth_required(self, client: TestClient):
        """Test that routes-simple is publicly accessible."""
        response = client.get("/routes-simple")

        assert response.status_code == 200
        # Should work without authentication

    def test_routes_simple_text_response(self, client: TestClient):
        """Test that routes-simple returns plain text."""
        response = client.get("/routes-simple")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/plain")

    def test_routes_simple_includes_institution_routes(self, client: TestClient):
        """Test that routes include institution endpoints."""
        response = client.get("/routes-simple")

        assert response.status_code == 200
        data = response.text.lower()

        assert "institution" in data

    def test_routes_simple_includes_scholarship_routes(self, client: TestClient):
        """Test that routes include scholarship endpoints."""
        response = client.get("/routes-simple")

        assert response.status_code == 200
        data = response.text.lower()

        assert "scholarship" in data

    def test_routes_simple_includes_tracking_routes(self, client: TestClient):
        """Test that routes include tracking endpoints."""
        response = client.get("/routes-simple")

        assert response.status_code == 200
        data = response.text.lower()

        assert "tracking" in data or "application" in data


class TestSystemEndpointsSecurity:
    """Security tests for system endpoints"""

    def test_endpoints_dont_expose_secrets(self, client: TestClient):
        """Test that system endpoints don't expose sensitive information."""
        endpoints = ["/", "/health", "/routes-simple"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200

            # Get response content as text
            if endpoint == "/routes-simple":
                data_str = response.text.lower()
            else:
                data_str = str(response.json()).lower()

            # Should not contain sensitive information
            sensitive_terms = [
                "password",
                "secret",
                "api_key",
                "token",
                "database_url",
                "connection_string",
            ]
            for term in sensitive_terms:
                assert (
                    term not in data_str
                ), f"Found sensitive term '{term}' in {endpoint}"

    def test_endpoints_handle_trailing_slash(self, client: TestClient):
        """Test that endpoints handle trailing slashes appropriately."""
        response_without = client.get("/health")
        response_with = client.get("/health/")

        # Both should work or redirect appropriately
        assert response_without.status_code in [200, 307, 308]
        assert response_with.status_code in [200, 307, 308]

    def test_endpoints_cors_headers(self, client: TestClient):
        """Test CORS headers on public endpoints."""
        response = client.get("/health")

        # May or may not have CORS headers depending on configuration
        # Just verify the request succeeds
        assert response.status_code == 200


class TestSystemEndpointsAvailability:
    """Availability tests for system endpoints"""

    def test_all_system_endpoints_available(self, client: TestClient):
        """Test that all system endpoints are available."""
        endpoints = [("/", 200), ("/health", 200), ("/routes-simple", 200)]

        for endpoint, expected_status in endpoints:
            response = client.get(endpoint)
            assert (
                response.status_code == expected_status
            ), f"Endpoint {endpoint} returned {response.status_code} instead of {expected_status}"

    def test_system_endpoints_uptime(self, client: TestClient):
        """Test system endpoints respond consistently."""
        # Make multiple requests to verify consistency
        for _ in range(3):
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data

    def test_system_endpoints_concurrent_requests(self, client: TestClient):
        """Test system endpoints handle concurrent requests."""
        import concurrent.futures

        def make_request():
            response = client.get("/health")
            return response.status_code

        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert all(status == 200 for status in results)


class TestSystemEndpointsErrorHandling:
    """Error handling tests for system endpoints"""

    def test_invalid_http_method_on_health(self, client: TestClient):
        """Test health endpoint with invalid HTTP method."""
        response = client.post("/health")

        # Should return method not allowed
        assert response.status_code in [405, 404]

    def test_invalid_http_method_on_routes(self, client: TestClient):
        """Test routes-simple endpoint with invalid HTTP method."""
        response = client.post("/routes-simple")

        # Should return method not allowed
        assert response.status_code in [405, 404]

    def test_malformed_request_to_health(self, client: TestClient):
        """Test health endpoint with malformed request."""
        response = client.get("/health", headers={"Accept": "invalid/type"})

        # Should still return 200 (health check should be resilient)
        assert response.status_code == 200
