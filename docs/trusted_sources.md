# Trusted Sources

Harbor should only answer factual Ontario healthcare navigation questions from approved official or public healthcare sources.

The first source registry lives at:

- `backend/app/ingestion/trusted_sources.json`

Initial approved source groups:

- Ontario government healthcare pages
- Health811 Ontario
- Ontario Health

Step 6 only defines the registry. It does not crawl, approve new domains dynamically, or index source content.

Step 7 adds URL allowlist checks so future crawler code can reject unapproved domains and paths before any network fetch happens.

Step 8 adds the fetch-free extraction contract for converting already-fetched HTML into clean page text and metadata.

Step 9 adds guarded single-page fetching. Fetching still requires a URL to pass the trusted source allowlist first.

Step 10 composes guarded fetching with extraction for one approved page. It still does not recursively crawl or index content.

Step 11 adds metadata-aware chunking for extracted pages. It still does not generate embeddings or index content.

Candidate later additions:

- Public Health Ontario pages
- Settlement and newcomer service pages when clearly public and explicitly approved
