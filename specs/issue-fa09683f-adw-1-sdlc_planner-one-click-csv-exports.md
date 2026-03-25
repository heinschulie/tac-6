# Feature: One Click CSV Exports

## Metadata
issue_number: `fa09683f`
adw_id: `1`
issue_json: ``

## Feature Description
Add one-click CSV export functionality for both available tables and query results. Users can download any uploaded table as a CSV file directly from the tables list, and can also export query results as CSV from the results panel. Two new backend endpoints serve the CSV data, and download buttons are added to the frontend UI.

## User Story
As a user
I want to export tables and query results as CSV files with a single click
So that I can quickly get my data out of the application for use in spreadsheets or other tools

## Problem Statement
Users can upload and query data but have no way to export it back out. They need a simple way to download table data and query results as CSV files.

## Solution Statement
Add two new GET/POST endpoints (`/api/table/{table_name}/export` for table export, `/api/export-results` for query result export) that return CSV responses. Add download icon buttons in the frontend: one next to each table's × remove button, and one next to the Hide button on query results.

## Relevant Files
Use these files to implement the feature:

- `app/server/server.py` - Add two new export endpoints here following existing endpoint patterns
- `app/server/core/sql_processor.py` - Use `execute_sql_safely()` for fetching table data
- `app/server/core/sql_security.py` - Use `validate_identifier()` and `check_table_exists()` for table name validation
- `app/server/core/data_models.py` - May need a request model for result export
- `app/client/index.html` - Add download buttons to table items and results header
- `app/client/src/main.ts` - Add download button creation logic and click handlers
- `app/client/src/api/client.ts` - Add API functions for export endpoints
- `app/client/src/style.css` - Add styles for download buttons
- `app/client/src/types.d.ts` - Add any new type definitions
- `app/server/tests/` - Add tests for new endpoints
- `README.md` - Reference for project structure and existing API endpoints
- `.claude/commands/test_e2e.md` - Read to understand E2E test execution
- `.claude/commands/e2e/test_basic_query.md` - Read to understand E2E test file format

### New Files
- `.claude/commands/e2e/test_csv_export.md` - E2E test for CSV export functionality

## Implementation Plan
### Phase 1: Foundation
Add the backend export endpoints. The table export endpoint fetches all rows from a validated table and returns CSV. The results export endpoint accepts columns + results payload and returns CSV.

### Phase 2: Core Implementation
Add download buttons to the frontend UI. Place a download icon button directly left of the × icon on each table item, and directly left of the Hide button on query results. Wire up click handlers to call the export endpoints and trigger browser file downloads.

### Phase 3: Integration
Add styling for the new buttons, write backend tests, create E2E test, and validate everything works end-to-end.

## Step by Step Tasks

### Step 1: Add table export endpoint to backend
- In `app/server/server.py`, add a new `GET /api/table/{table_name}/export` endpoint
- Use `validate_identifier()` to validate the table name
- Use `execute_sql_safely()` to fetch all rows: `SELECT * FROM [{table_name}]`
- Use Python's `csv` module with `io.StringIO` to generate CSV content from columns and rows
- Return a `StreamingResponse` with `media_type="text/csv"` and `Content-Disposition: attachment; filename="{table_name}.csv"` header
- Import `StreamingResponse` from `starlette.responses`

### Step 2: Add query results export endpoint to backend
- In `app/server/server.py`, add a new `POST /api/export-results` endpoint
- Accept a JSON body with `columns: list[str]` and `results: list[dict]` (create a Pydantic model `ExportResultsRequest` in `data_models.py`)
- Use Python's `csv` module with `io.StringIO` to generate CSV from the provided data
- Return a `StreamingResponse` with `media_type="text/csv"` and `Content-Disposition: attachment; filename="query_results.csv"` header

### Step 3: Add backend tests for export endpoints
- Add tests in existing test files or a new test file for:
  - Table export returns valid CSV with correct headers
  - Table export with invalid/nonexistent table returns error
  - Results export returns valid CSV matching input data
  - Results export with empty data works correctly

### Step 4: Add API client functions in frontend
- In `app/client/src/api/client.ts`, add:
  - `exportTable(tableName: string)` - fetches `GET /api/table/{tableName}/export` and triggers download
  - `exportResults(columns: string[], results: Record<string, unknown>[])` - fetches `POST /api/export-results` and triggers download
- These functions should fetch the response as a blob, create a temporary URL, and trigger a download via a temporary `<a>` element

### Step 5: Add download buttons to the UI
- In `app/client/src/main.ts`, in the `displayTables()` function:
  - Add a download button directly left of the existing × (remove) button in each `.table-header`
  - Use an appropriate download icon (↓ arrow or SVG download icon)
  - Add click handler that calls `exportTable(tableName)`
- In `app/client/src/main.ts`, in the `displayResults()` function:
  - Add a download button directly left of the Hide/Show toggle button in `#results-header`
  - Store current results/columns in module-level variables so the download handler can access them
  - Add click handler that calls `exportResults(columns, results)`

### Step 6: Add styles for download buttons
- In `app/client/src/style.css`, add styles for the download buttons
- Style them consistently with existing buttons (match the × button style for tables, match the toggle button style for results)
- Ensure proper hover/active states

### Step 7: Create E2E test file
- Create `.claude/commands/e2e/test_csv_export.md` following the format of `test_basic_query.md`
- Test steps should:
  1. Navigate to the app
  2. Verify a table exists in Available Tables
  3. Verify a download button appears next to the × icon
  4. Click the table download button and verify download triggers
  5. Run a query to get results
  6. Verify a download button appears next to the Hide button
  7. Click the results download button and verify download triggers
  8. Take screenshots at key steps

### Step 8: Run validation commands
- Execute all validation commands listed below to confirm zero regressions

## Testing Strategy
### Unit Tests
- Test table export endpoint returns 200 with valid CSV content-type and Content-Disposition header
- Test table export with nonexistent table returns 404
- Test table export with invalid table name returns 400
- Test results export with valid columns/results returns correct CSV
- Test results export with empty results returns CSV with headers only

### Edge Cases
- Exporting a table with no rows (should return CSV with headers only)
- Exporting results with special characters in data (commas, quotes, newlines)
- Exporting a table with a name that needs escaping
- Large table export performance
- Results export with empty columns list

## Acceptance Criteria
- Download button visible next to each table's × icon in Available Tables
- Download button visible next to the Hide button in Query Results
- Clicking table download button downloads a valid CSV file named `{table_name}.csv`
- Clicking results download button downloads a valid CSV file named `query_results.csv`
- CSV files contain correct headers and data
- All existing tests pass with zero regressions
- Frontend builds without TypeScript errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_csv_export.md` to validate CSV export functionality works
- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend tests to validate the feature works with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the feature works with zero regressions

## Notes
- Python's built-in `csv` module is sufficient; no new dependencies needed
- `StreamingResponse` from starlette is already available via FastAPI
- For the download icon, use a simple SVG or Unicode character (⬇ or similar) consistent with the existing × icon approach
- The results export endpoint accepts pre-computed results rather than re-executing SQL, avoiding security concerns with storing/replaying queries
