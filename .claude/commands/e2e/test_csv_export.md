# E2E Test: CSV Export Functionality

Test one-click CSV export for tables and query results.

## User Story

As a data analyst
I want to export tables and query results as CSV files with one click
So that I can quickly get data out of the application for use in spreadsheets

## Test Steps

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the page loads with "Natural Language SQL Interface" title

4. Click the "Upload Data" button
5. Click the "Product Inventory" sample data button
6. **Verify** the upload modal closes and the "products" table appears in Available Tables
7. Take a screenshot showing the table with download button

8. **Verify** a download button (↓) appears to the left of the × button on the products table
9. Click the download button (↓) on the products table
10. **Verify** a CSV file download is triggered (check network requests for /api/table/products/export returning 200)
11. Take a screenshot after clicking the table download button

12. Enter the query: "Show me all products"
13. Click the Query button
14. Wait for results to appear
15. **Verify** query results are displayed with a results table
16. **Verify** a download button (↓) appears in the results header, left of the Hide button
17. Take a screenshot showing query results with the download button

18. Click the download button (↓) in the results header
19. **Verify** a CSV file download is triggered (check network requests for /api/export-results returning 200)
20. Take a screenshot after clicking the results download button

## Success Criteria
- Products table appears after upload with download button visible
- Table download button triggers CSV export (200 response from /api/table/products/export)
- Query results display with download button visible
- Results download button triggers CSV export (200 response from /api/export-results)
- 4 screenshots are taken
