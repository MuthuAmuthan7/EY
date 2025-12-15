# Migration Guide: OpenAI to Google Gemini

This document explains the changes made to migrate the RFP Automation Platform from OpenAI to Google Gemini.

## Changes Summary

### 1. Dependencies (`requirements.txt`)
**Removed:**
- `openai>=1.3.0`
- `tiktoken>=0.5.1`

**Added:**
- `google-generativeai>=0.3.0`
- `llama-index-llms-gemini>=0.1.0`
- `llama-index-embeddings-gemini>=0.1.0`

### 2. Environment Variables (`.env`)
**Changed:**
- `OPENAI_API_KEY` → `GOOGLE_API_KEY`
- `LLM_MODEL` default: `gpt-4-turbo-preview` → `gemini-1.5-pro`

### 3. Configuration (`src/config.py`)
**Changed:**
- Field name: `openai_api_key` → `google_api_key`
- Default model: `gemini-1.5-pro`

### 4. LLM Client (`src/llm/client.py`)
**Major Rewrite:**
- Replaced `openai` SDK with `google.generativeai`
- Updated `chat_completion()` to use Gemini's API
- Maintained same interface for compatibility

**Key Changes:**
```python
# Before (OpenAI)
from openai import OpenAI
self.client = OpenAI(api_key=self.api_key)

# After (Gemini)
import google.generativeai as genai
genai.configure(api_key=self.api_key)
self.model = genai.GenerativeModel(self.model_name)
```

### 5. Index Builder (`src/data_ingestion/build_indexes.py`)
**Changed:**
- Replaced `OpenAI` and `OpenAIEmbedding` with `Gemini` and `GeminiEmbedding`
- Updated embedding model: `models/embedding-001`

**Key Changes:**
```python
# Before (OpenAI)
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

Settings.llm = OpenAI(model=..., api_key=...)
Settings.embed_model = OpenAIEmbedding(api_key=...)

# After (Gemini)
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

Settings.llm = Gemini(model=..., api_key=...)
Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001", api_key=...)
```

### 6. Documentation Updates
- `README.md`: Updated all references to OpenAI → Gemini
- `SETUP.md`: Updated API key instructions
- `web/app.py`: Updated sidebar "About" section

## Setup Instructions After Migration

1. **Get Google API Key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Enable Gemini API if not already enabled

2. **Update Environment:**
   ```bash
   # Edit .env file
   GOOGLE_API_KEY=your-google-api-key-here
   LLM_MODEL=gemini-1.5-pro
   ```

3. **Reinstall Dependencies:**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

4. **Rebuild Indexes:**
   ```bash
   # Indexes need to be rebuilt with Gemini embeddings
   python -m src.data_ingestion.build_indexes
   ```

5. **Run Application:**
   ```bash
   streamlit run web/app.py
   ```

## API Differences

### Rate Limits
- **OpenAI GPT-4**: ~10,000 TPM (tokens per minute)
- **Gemini 1.5 Pro**: 2 RPM (requests per minute) free tier, higher with paid

### Context Window
- **OpenAI GPT-4 Turbo**: 128K tokens
- **Gemini 1.5 Pro**: 1M tokens (much larger!)

### Pricing (as of Dec 2024)
- **OpenAI GPT-4 Turbo**: $10/1M input tokens, $30/1M output tokens
- **Gemini 1.5 Pro**: Free tier available, then $3.50/1M input tokens, $10.50/1M output tokens

### Response Format
- Both support JSON mode
- Gemini may require more explicit JSON formatting instructions

## Benefits of Gemini

1. **Larger Context Window**: 1M tokens vs 128K
2. **Cost Effective**: Lower pricing, free tier available
3. **Multimodal**: Native support for images, audio, video
4. **Fast**: Generally faster response times

## Potential Issues & Solutions

### Issue: JSON Parsing Errors
**Solution:** The LLM client already handles markdown code block extraction. If issues persist, adjust the prompt to be more explicit about JSON formatting.

### Issue: Rate Limiting
**Solution:** Implement exponential backoff or use paid tier for higher limits.

### Issue: Different Response Style
**Solution:** Adjust system prompts in `src/llm/prompts.py` if Gemini's responses differ significantly from OpenAI's.

## Rollback Instructions

If you need to revert to OpenAI:

1. Restore old `requirements.txt` (use git)
2. Change `.env`: `GOOGLE_API_KEY` → `OPENAI_API_KEY`
3. Restore old versions of:
   - `src/config.py`
   - `src/llm/client.py`
   - `src/data_ingestion/build_indexes.py`
4. Rebuild indexes with OpenAI embeddings

## Testing Checklist

- [ ] LLM client initializes without errors
- [ ] Index building completes successfully
- [ ] RFP scanning works
- [ ] Technical agent returns spec matches
- [ ] Pricing agent calculates costs
- [ ] Master agent generates narratives
- [ ] UI displays results correctly
- [ ] JSON export works

## Notes

- All agent logic remains unchanged
- Service layer unchanged
- Data models unchanged
- Only LLM provider changed
- Existing parsed RFPs and data files are compatible
