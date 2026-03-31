# Secure Document Retrieval Q&A App

## Structure

```text
app.py
startup.txt
requirements.txt
.env.example
aegis_app/
  __init__.py
  config.py
  templates/
    index.html
  routes/
    main.py
    upload.py
  services/
    agent.py
    audit.py
    authz.py
    azure_clients.py
    ingest.py
    llm.py
    retrieval.py
    storage.py
```

## Environment variables
Use `.env.example` as your checklist in App Service Configuration.

## Notes
- Uses Managed Identity via `DefaultAzureCredential`
- Uploads raw docs to `RAW_DOCS_CONTAINER`
- Stores processed chunk JSON in `PROCESSED_DOCS_CONTAINER`
- Retrieves keyword-matched chunks and sends only those chunks to Azure OpenAI
- Returns citations for retrieved chunks
