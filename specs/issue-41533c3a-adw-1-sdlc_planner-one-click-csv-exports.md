# Feature: One Click CSV Exports

## Metadata
issue_number: `41533c3a`
adw_id: `1`
issue_json: `{"number":1,"title":"One click exports","body":"using adw_pan_build_review create one click table exports and one click result export feature to get data as csv files \n\nCreate two new endpoints to support these features. One to to handle table exports and one to handle query result exports\n\nPlace a download button directly left of the 'x' icon for available tables \nPlace a download button directly left of the 'hide' button for query results \n\nUse an appropriate download icon "}`

## Feature Description
Add one-click CSV export functionality for both database tables and query results. Users can download any available table as a CSV file directly from the tables list, and export query results as CSV from the results panel. Two new backend endpoints handle the CSV generation, and two new download buttons in the UI trigger browser downloads.

## User Story
As a data analyst
I want to export tables and query results as CSV files with one click
So that I can quickly get data out of the application for use in spreadsheets or other tools

## Problem Statement
Users can query and view data in the application but have no way to export it. They must manually copy data or re-query outside the app to get CSV files.

## Solution Statement
Add two new API endpoints (`GET /api/table/{table_name}/export` for table exports, `POST /api/export-results` for query result exports) that return CSV file responses. Add download buttons in the UI next to existing controls—left of the × icon for tables and left of the Hide button for results.

## Relevant Files
Use these files to implement the feature:

- `app/server/server.py` — Add new export endpoints here, following existing endpoint patterns
- `app/server/core/data_models.py` — Add `ExportResultsRequest` model for the results export endpoint
- `app/server/core/sql_processor.py` — Use `execute_sql_safely()` to fetch table data for export
- `app/server/core/sql_security.py` — Use `validate_identifier()` and `check_table_exists()` for table name validation
- `app/server/tests/` — Add tests for new export endpoints
- `app/client/index.html` — Add download button next to Hide button in results header
- `app/client/src/main.ts` — Add download button creation in `displayTables()`, add click handlers for both export buttons, add `exportTable()` and `exportResults()` functions
- `app/client/src/api/client.ts` — Add `exportTable(tableName)` and `exportResults(columns, results)` methods to `api` object
- `app/client/src/style.css` — Add styles for `.download-table-button` and `.download-results-button`
- `app/client/src/types.d.ts` — Add `ExportResultsRequest` interface
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand E2E test format

### New Files
- `app/server/tests/test_csv_export.py` — Unit tests for CSV export endpoints
- `.claude/commands/e2e/test_csv_export.md` — E2E test for CSV export functionality

## Implementation Plan
### Phase 1: Foundation
Add the `ExportResultsRequest` data model and implement the two backend CSV export endpoints with proper validation and security checks. Add backend unit tests.

### Phase 2: Core Implementation
Add frontend API client methods, create download buttons in the UI with appropriate styling and icons, and wire up click handlers that trigger browser file downloads.

### Phase 3: Integration
Verify end-to-end flow works: clicking download buttons triggers API calls, browser downloads CSV files with correct content and filenames. Run all tests to ensure zero regressions.

## Step by Step Tasks

### Step 1: Add ExportResultsRequest model
- In `app/server/core/data_models.py`, add:
  ```python
  class ExportResultsRequest(BaseModel):
      columns: List[str]
      results: List[Dict[str, Any]]
  ```

### Step 2: Add table export endpoint
- In `app/server/server.py`, add `GET /api/table/{table_name}/export` endpoint
- Validate table name with `validate_identifier(table_name, "table")`
- Check table exists with `check_table_exists()`
- Use `execute_sql_safely(f"SELECT * FROM {table_name}")` to get all data
- Build CSV using Python's `csv` module and `io.StringIO`
- Return `StreamingResponse` with `Content-Type: text/csv` and `Content-Disposition: attachment; filename="{table_name}.csv"`

### Step 3: Add query results export endpoint
- In `app/server/server.py`, add `POST /api/export-results` endpoint
- Accept `ExportResultsRequest` body
- Build CSV from provided columns and results using `csv` module and `io.StringIO`
- Return `StreamingResponse` with `Content-Type: text/csv` and `Content-Disposition: attachment; filename="query_results.csv"`

### Step 4: Add backend tests
- Create `app/server/tests/test_csv_export.py`
- Test table export: valid table returns CSV with correct headers and data
- Test table export: nonexistent table returns 404 or error
- Test table export: invalid table name (SQL injection) returns validation error
- Test results export: valid columns/results returns correct CSV
- Test results export: empty results returns CSV with headers only

### Step 5: Create E2E test file
- Create `.claude/commands/e2e/test_csv_export.md` following the pattern from `test_basic_query.md`
- Test steps: upload a CSV file, verify table appears, click table download button, verify download triggers
- Test steps: run a query, verify results appear, click results download button, verify download triggers
- Include screenshot steps at key moments

### Step 6: Add frontend API methods
- In `app/client/src/api/client.ts`, add to the `api` object:
  - `exportTable(tableName: string)` — `GET /api/table/${tableName}/export`, trigger browser download via blob URL
  - `exportResults(columns: string[], results: Record<string, any>[])` — `POST /api/export-results`, trigger browser download via blob URL
- Both methods should create a temporary `<a>` element with blob URL, click it, then revoke the URL

### Step 7: Add TypeScript types
- In `app/client/src/types.d.ts`, add `ExportResultsRequest` interface with `columns: string[]` and `results: Record<string, any>[]`

### Step 8: Add download button for tables
- In `app/client/src/main.ts` in the `displayTables()` function:
  - Create a download button element before the remove button: `const downloadButton = document.createElement('button')`
  - Set `className = 'download-table-button'`
  - Use `innerHTML = '↓'` (downward arrow unicode character) as download icon
  - Set `title = 'Export as CSV'`
  - Add click handler calling `api.exportTable(table.name)` (or a wrapper function)
  - Insert before the remove button in `tableHeader`

### Step 9: Add download button for query results
- In `app/client/index.html`, add a download button in the `.results-header` div, directly left of the Hide button
  - `<button id="download-results" style="display: none;" title="Export as CSV">↓</button>`
- In `app/client/src/main.ts`:
  - Store current query results (columns and results) in module-level variables when `displayResults()` is called
  - Show the download-results button when results are displayed
  - Hide it when results are cleared
  - Add click handler that calls `api.exportResults(currentColumns, currentResults)`

### Step 10: Add CSS styles
- In `app/client/src/style.css`, add styles for `.download-table-button`:
  - Match `.remove-table-button` style but with primary/neutral color scheme
  - On hover, use a blue/primary highlight instead of red
- Add styles for `#download-results`:
  - Match the toggle-results button style
  - Consistent sizing and spacing

### Step 11: Run validation commands
- Run all validation commands listed below to ensure zero regressions

## Testing Strategy
### Unit Tests
- Test `GET /api/table/{table_name}/export` returns valid CSV with correct headers and row data
- Test `GET /api/table/{table_name}/export` with nonexistent table returns appropriate error
- Test `GET /api/table/{table_name}/export` with invalid/malicious table name is rejected
- Test `POST /api/export-results` returns valid CSV matching provided columns and results
- Test `POST /api/export-results` with empty results returns headers-only CSV

### Edge Cases
- Table with no rows — should return CSV with headers only
- Table/column names with special characters — should be handled by existing validation
- Very large table export — streaming response handles memory efficiently
- Results with missing keys in some rows — CSV should handle gracefully with empty cells
- Empty columns list in export-results request

## Acceptance Criteria
- Clicking the download button on a table triggers a CSV file download named `{table_name}.csv` containing all table data
- Clicking the download button on query results triggers a CSV file download named `query_results.csv` containing displayed results
- Download buttons are visually consistent with existing UI, placed left of their respective existing buttons
- Download buttons use a recognizable download icon (↓)
- All existing tests pass with zero regressions
- Frontend builds without TypeScript errors
- New backend endpoints have unit test coverage

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && npx tsc --noEmit` - Run frontend type check to validate no TypeScript errors
- `cd app/client && npm run build` - Run frontend build to validate the feature compiles correctly
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_csv_export.md` E2E test to validate this functionality works

## Notes
- No new Python dependencies needed — `csv` and `io` are stdlib modules, `StreamingResponse` is available from `starlette.responses` (included with FastAPI)
- Using `↓` (unicode downward arrow) as the download icon keeps consistency with the existing `×` pattern for the remove button — no icon library needed
- The results export endpoint accepts columns/results in the request body rather than re-executing the query, ensuring the exported data matches exactly what the user sees
