# AIA System Test Plan

This document outlines the testing strategy for the AIA system's API. It is based on an analysis of `aia/api/full_api.py` and the schemas in `aia/schemas/`.

## 1. Test Structure

Tests will be organized into a new `tests/api/` directory, mirroring the API structure:

- `tests/api/test_main.py`: For general endpoints like `/`, `/health`, and `/metrics`.
- `tests/api/test_auth.py`: For authentication endpoints (`/auth/*`).
- `tests/api/test_mcp.py`: For Model Control Protocol endpoints (`/api/v1/mcp/*`).
- `tests/api/test_economic.py`: For economic governance endpoints (`/economic/*`).
- `tests/api/test_dkg.py`: For Dynamic Knowledge Graph endpoints (`/dkg/*`).
- `tests/api/test_performance.py`: For performance management endpoints (`/performance/*`).
- `tests/api/test_venture.py`: For venture discovery endpoints (`/venture/*`).
- `tests/api/test_reports.py`: For structured reporting endpoints (`/reports/*`).
- `tests/api/test_dashboard.py`: For dashboard endpoints (`/api/v1/dashboard/*`).
- `tests/api/test_export.py`: For export endpoints (`/api/v1/export/*`).

## 2. Test Plan by Endpoint

### 2.1. Main Endpoints (`tests/api/test_main.py`)

#### `GET /`
- **Happy Path:**
  - `test_get_root_returns_200_and_system_info`: Verify a 200 OK response and the presence of key fields (`message`, `version`, `status`).
- **Edge Cases:**
  - `test_get_root_during_initialization`: Mock the system state to be "initializing" and verify the status field reflects this.

#### `GET /health`
- **Happy Path:**
  - `test_get_health_returns_200_and_healthy_status`: Verify a 200 OK response and `"status": "healthy"`.
- **Edge Cases:**
  - `test_get_health_when_not_initialized`: Mock system state to be uninitialized and verify a `"status": "degraded"` response.
  - `test_get_health_with_some_components_down`: Mock individual components as `None` and verify the `components` dictionary in the response is accurate.

#### `GET /ready`
- **Happy Path:**
  - `test_get_ready_returns_200_when_initialized`: Verify a 200 OK response when the system is fully initialized.
- **Failure Cases:**
  - `test_get_ready_returns_503_when_not_initialized`: Verify a 503 Service Unavailable response when the system is not initialized.
  - `test_get_ready_returns_503_when_critical_components_missing`: Mock critical components (`mas_system`, `economic_governor`) as `None` and verify a 503 response.

#### `POST /process`
- **Happy Path:**
  - `test_process_general_task`: Submit a valid `EnhancedTaskRequest` with `task_type="general"` and verify a successful `TaskStatusResponse`.
  - `test_process_economic_task`: Submit a task with `task_type="economic"` and verify it's routed correctly.
  - `test_process_dkg_task`: Submit a task with `task_type="dkg"` and verify it's routed correctly.
- **Validation Errors:**
  - `test_process_invalid_request_body`: Send a request with missing required fields (`id`, `description`) and verify a 422 Unprocessable Entity response.
- **Failure Cases:**
  - `test_process_task_when_system_not_ready`: Send a request when the system is not initialized and verify a 503 response.
  - `test_process_task_with_unavailable_subsystem`: Send a task for a subsystem (e.g., "economic") that is mocked as `None` and verify a 503 response.

### 2.2. Authentication Endpoints (`tests/api/test_auth.py`)

- **Setup:** Use a test database and mock the `auth_manager`.

#### `POST /auth/register`
- **Happy Path:**
  - `test_register_user_success`: Register a new user with valid data and verify a 200 OK response and the correct `User` model is returned.
- **Validation Errors:**
  - `test_register_user_invalid_email`: Attempt to register with an invalid email format and verify a 422 response.
  - `test_register_user_password_too_short`: Attempt to register with a short password and verify a 422 response.
- **Failure Cases:**
  - `test_register_user_email_already_exists`: Attempt to register an email that already exists and verify a 400 Bad Request response.

#### `POST /auth/login`
- **Happy Path:**
  - `test_login_user_success`: Log in with valid credentials and verify a 200 OK response with a `Token` model.
- **Failure Cases:**
  - `test_login_user_invalid_email`: Attempt to log in with a non-existent email and verify a 401 Unauthorized response.
  - `test_login_user_incorrect_password`: Attempt to log in with a correct email but incorrect password and verify a 401 response.

#### `GET /auth/me`
- **Happy Path:**
  - `test_get_current_user_info`: Provide a valid JWT and verify a 200 OK response with the correct `User` data.
- **Authorization:**
  - `test_get_current_user_no_token`: Make a request without a token and verify a 401 Unauthorized response.
  - `test_get_current_user_invalid_token`: Make a request with an invalid or expired token and verify a 401 response.

### 2.3. MCP Endpoints (`tests/api/test_mcp.py`)

#### `POST /api/v1/mcp/process`
- **Happy Path:**
  - `test_mcp_process_success`: Send a valid `MCPRequest` and verify a 202 Accepted response with a `task_id`.
- **Authorization:**
  - `test_mcp_process_requires_auth`: Attempt to access the endpoint without a valid token and verify a 401 response.

#### `GET /api/v1/mcp/status/{task_id}`
- **Happy Path:**
  - `test_get_mcp_status_processing`: Check the status of a running task and verify a 200 OK response with `"status": "processing"`.
  - `test_get_mcp_status_completed`: Check the status of a completed task and verify a 200 OK response with `"status": "completed"`.
- **Authorization:**
  - `test_get_mcp_status_requires_auth`: Attempt to access without a token and verify 401.
  - `test_get_mcp_status_forbids_other_user`: Attempt to access a task owned by another user and verify a 403 Forbidden response.
- **Failure Cases:**
  - `test_get_mcp_status_not_found`: Use a non-existent `task_id` and verify a 404 Not Found response.

### 2.4. Economic Endpoints (`tests/api/test_economic.py`)

- **Setup:** Mock the `economic_governor`.

#### `POST /economic/distribute`
- **Happy Path:**
  - `test_distribute_tokens_success`: Send a valid `EconomicRequest` and verify a 200 OK response.
- **Validation Errors:**
  - `test_distribute_tokens_missing_amount`: Send a request without the `amount` and verify a 422 response.

### 2.5. DKG Endpoints (`tests/api/test_dkg.py`)

- **Setup:** Mock the `dkg_manager`.

#### `POST /dkg/query`
- **Happy Path:**
  - `test_dkg_query_success`: Send a valid `DKGRequest` and verify a 200 OK response with the expected knowledge structure.
- **Validation Errors:**
  - `test_dkg_query_invalid_query_type`: Send a request with an invalid `query_type` and verify a 422 response.

### 2.6. Performance Endpoints (`tests/api/test_performance.py`)

- **Setup:** Mock the `performance_tracker`.

#### `POST /performance/record`
- **Happy Path:**
  - `test_record_performance_metric_success`: Send a valid `PerformanceRequest` and verify a 200 OK response.

#### `GET /performance/rankings`
- **Happy Path:**
  - `test_get_performance_rankings_success`: Verify a 200 OK response and a list of rankings.

### 2.7. Venture Endpoints (`tests/api/test_venture.py`)

- **Setup:** Mock the `venture_discovery`.

#### `POST /venture/discover`
- **Happy Path:**
  - `test_discover_ventures_success`: Send a valid `VentureRequest` and verify a 200 OK response.

### 2.8. Reporting Endpoints (`tests/api/test_reports.py`)

- **Setup:** Mock the `structured_report_generator`.

#### `POST /reports/structured`
- **Happy Path:**
  - `test_generate_structured_report_success`: Send a valid `StructuredReportRequest` and verify a 202 Accepted response with a `report_id`.

#### `GET /reports/{report_id}/status`
- **Happy Path:**
  - `test_get_report_status_success`: Check the status of a report and verify a 200 OK response.
- **Failure Cases:**
  - `test_get_report_status_not_found`: Use an invalid `report_id` and verify a 404 response.

#### `GET /reports/{report_id}/results`
- **Happy Path:**
  - `test_get_report_results_success`: Get the results of a completed report and verify a 200 OK response.
- **Failure Cases:**
  - `test_get_report_results_not_completed`: Attempt to get results for a report that is still processing and verify a 400 Bad Request response.
