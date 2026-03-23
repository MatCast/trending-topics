## Extractions Debugging Plan

We are adding an insights/warnings system to extractions to help users understand why an extraction might have returned 0 results.

### Subagent Split
- **Backend Subagent**: Update data models, parser base class, and `researcher.py` to collect and save `insights` to the Firestore `extractions` document.
- **Frontend Subagent**: Update the Nuxt UI (`[id].vue` extractions page) to gracefully display the `insights` array returned by the API.

### Interface (API Contract)
The Extraction document in Firestore and the FastAPI `ExtractionResponse` will include a new `insights` array. Each object will be:
```json
{
  "source_id": "reddit",
  "source_name": "r/SaaS",
  "type": "warning", // "error", "warning", "info"
  "message": "Fetched 25 items but 0 matched your keywords."
}
```

The parsers will accrue these insights internally during execution, and `researcher.py` will read them and save them via `firebase_client.py`.
