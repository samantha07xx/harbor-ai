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

Candidate later additions:

- Public Health Ontario pages
- Settlement and newcomer service pages when clearly public and explicitly approved
