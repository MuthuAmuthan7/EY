# Setup Instructions

## Quick Start

1. **Navigate to project directory**
   ```bash
   cd d:\Projects\EY\rfp-agentic-platform
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   copy .env.example .env
   ```
   
   Edit `.env` and add your Google API key:
   ```
   GOOGLE_API_KEY=your-google-api-key-here
   ```

5. **Build vector indexes**
   ```bash
   python -m src.data_ingestion.build_indexes
   ```

6. **Run the application**
   ```bash
   streamlit run web/app.py
   ```

## Verification

After running the app, you should see:
- Streamlit UI opens in browser
- "All agents ready" status in sidebar
- Sample RFP available when you click "Scan RFPs"

## Troubleshooting

**If indexes fail to build:**
- Ensure Google API key is valid and Gemini API is enabled
- Check internet connection
- Verify data files exist in `data/` directories

**If import errors occur:**
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`
- Ensure Python 3.11+ is installed

**If Streamlit doesn't start:**
- Check if port 8501 is available
- Try: `streamlit run web/app.py --server.port 8502`
