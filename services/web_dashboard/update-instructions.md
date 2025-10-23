# Dashboard Update Instructions

I've created an updated version of the `dashboard-modular.js` file that shows the source of data updates in the console logs. The updated file is located at:

```
c:\Users\kmohn\New folder\AWS_Cloud\services\web_dashboard\static\js\dashboard-modular-updated.js
```

## Changes Made

1. Added source information to WebSocket data updates:
   - Changed `console.log('📈 Received dashboard stats update:', data);` to
     `console.log('📈 Received dashboard stats update [Source: WebSocket Real-time]:', data);`

2. Added source information to REST API data updates:
   - Added `console.log('📈 Received dashboard stats update [Source: REST API Fetch]:', data);` 
     at the end of the `updateDashboardStats` method

3. Added source information to all other WebSocket update messages:
   - Patient updates: Added `[Source: WebSocket Real-time]` to console logs
   - System status updates: Added `[Source: WebSocket Real-time]` to console logs
   - Alerts updates: Added `[Source: WebSocket Real-time]` to console logs

4. Added source information to dynamic WebSocket loading:
   - In `setupWebSocketAfterLoad` method, added `[Source: WebSocket Dynamic Load]` to console logs

## How to Apply the Changes

You have two options to apply these changes:

### Option 1: Replace the existing file
1. Rename the updated file to replace the original:
   ```powershell
   Rename-Item -Path "c:\Users\kmohn\New folder\AWS_Cloud\services\web_dashboard\static\js\dashboard-modular-updated.js" -NewName "c:\Users\kmohn\New folder\AWS_Cloud\services\web_dashboard\static\js\dashboard-modular.js" -Force
   ```

### Option 2: Make the changes manually
1. Open the original `dashboard-modular.js` file
2. Search for each instance of `console.log('📈 Received dashboard stats update:'` and add the source information
3. Search for the `updateDashboardStats` method and add the source log at the end
4. Make the same changes for other data update types (patients, system status, alerts)

## Testing the Changes

1. Restart your web application
2. Open your browser's developer console
3. Watch for the dashboard update messages that now include the source information
4. You'll now be able to see if updates are coming from:
   - `[Source: WebSocket Real-time]` - normal WebSocket connection
   - `[Source: WebSocket Dynamic Load]` - dynamically loaded WebSocket connection
   - `[Source: REST API Fetch]` - fallback to REST API polling

This will help you identify whether the data is coming from the real-time WebSocket connection or the fallback REST API polling mechanism.