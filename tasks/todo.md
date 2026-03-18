# Reddit Extraction 403 Bug Fix

## Plan
- [x] Investigate cause of 403 Forbidden specifically on Cloud Run.
- [x] Update User-Agent headers in `backend/app/parsers/reddit.py` to bypass strict datacenter IP blocking.
- [x] Verify fix by executing parser with updated headers.

## Review & Results
- **Reddit API**: Emulated a standard browser User-Agent in `reddit.py` to prevent 403 blocks from Google Cloud Run IPs.
