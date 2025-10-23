# Content Security Policy (CSP) Fix

## Issue Fixed
- **Problem**: Browser errors when loading source map files from CDNs
- **Cause**: Content Security Policy (CSP) blocking connections to external CDNs
- **Error Messages**:
  ```
  Refused to connect to 'https://cdn.jsdelivr.net/npm/chart.umd.min.js.map' because it violates the following Content Security Policy directive: "connect-src 'self' http://localhost:* http://127.0.0.1:* ws://localhost:* ws://127.0.0.1:* wss://localhost:* wss://127.0.0.1:*".
  ```

## Solution Implemented
Added `https://cdn.jsdelivr.net/` to the `connect-src` directive in the Content Security Policy in `base.html`.

## What is Content Security Policy (CSP)?
Content Security Policy is a security feature that helps prevent various types of attacks like Cross-Site Scripting (XSS) by specifying which resources (scripts, stylesheets, images, etc.) are allowed to be loaded by the browser.

## Why Source Maps Were Blocked
Source maps are files that help with debugging minified JavaScript and CSS. They map the minified code back to the original source code. These were being loaded from CDNs, but the CSP was blocking connections to those CDNs.

## Changes Made:
1. Updated the CSP meta tag in `base.html` to include `https://cdn.jsdelivr.net/` in the `connect-src` directive
2. This change aligns with the CSP header that was already set correctly in `app.py`

## Future Best Practices
1. **Consistency**: Keep CSP settings consistent between HTTP headers and meta tags
2. **Development vs. Production**: Consider having different CSP settings for development (with source maps) and production environments
3. **Monitoring**: Regularly check browser console for CSP violations

## Note on Source Maps
Source maps are primarily useful during development and debugging. For production deployments, you might want to disable them to improve performance and security. You can do this by configuring your bundler to not generate source maps for production builds.