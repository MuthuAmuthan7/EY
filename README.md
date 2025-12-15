# 🤖 Agentic AI RFP Automation Platform

An AI-driven system for automating Request for Proposal (RFP) processing using multi-agent orchestration with LangGraph, retrieval-augmented generation with LlamaIndex, and intelligent spec matching.

## 🎯 Overview

This platform automates the entire RFP response workflow for a cable manufacturing OEM:

1. **Sales Agent**: Scans URLs for RFPs, filters by deadline (next 3 months), and generates summaries
2. **Technical Agent**: Matches RFP specifications to product SKUs using vector search and computes SpecMatch%
3. **Pricing Agent**: Calculates material and testing costs with detailed breakdowns
4. **Master Agent**: Orchestrates the workflow and generates professional narrative responses

## ✨ Features

- 🔍 **Automated RFP Discovery**: Scans and filters relevant RFPs
- 🎯 **Intelligent Spec Matching**: Vector-based similarity search with tolerance-based comparison
- 💰 **Automated Pricing**: Material + testing cost calculation with proportional allocation
- 📊 **Interactive Dashboard**: Streamlit-based UI for workflow management
- 🤖 **Multi-Agent Orchestration**: Coordinated AI agents using LangGraph
- 📝 **AI-Generated Responses**: Professional narratives for RFP submissions

## 🏗️ Architecture

```
┌─────────────────┐
│   Streamlit UI  │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Master  │
    │  Agent  │
    └────┬────┘
         │
    ┌────┴────────────────┐
    │                     │
┌───▼───┐  ┌──────▼──────┐  ┌────▼────┐
│ Sales │  │  Technical  │  │ Pricing │
│ Agent │  │    Agent    │  │  Agent  │
└───┬───┘  └──────┬──────┘  └────┬────┘
    │             │              │
    │      ┌──────▼──────┐       │
    │      │ LlamaIndex  │       │
    │      │ Vector DB   │       │
    │      └─────────────┘       │
    │                            │
    └──────────┬─────────────────┘
               │
        ┌──────▼──────┐
        │   OpenAI    │
        │     LLM     │
        └─────────────┘
```

## 📦 Installation

### Prerequisites

- Python 3.11+
- Google API key (for Gemini)

### Setup

1. **Clone the repository**
   ```bash
   cd d:\Projects\EY
   cd rfp-agentic-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   copy .env.example .env
   # Edit .env and add your Google API key for Gemini
   ```

5. **Build vector indexes**
   ```bash
   python -m src.data_ingestion.build_indexes
   ```

## 🚀 Usage

### Running the Web Application

```bash
streamlit run web/app.py
```

The application will open in your browser at `http://localhost:8501`

### Workflow

1. **Scan RFPs**: Click "Scan RFPs" to discover available RFPs
2. **Select RFP**: Choose an RFP from the list
3. **Run Workflow**: Click "Run AI Workflow" to process the RFP
4. **View Results**: Explore technical matches and pricing in the tabs

## 📁 Project Structure

```
rfp-agentic-platform/
├── src/
│   ├── agents/          # AI agents (Sales, Technical, Pricing, Master)
│   ├── api/             # API schemas and DTOs
│   ├── data_ingestion/  # Data loaders and index builders
│   ├── llm/             # LLM client and prompts
│   ├── models/          # Pydantic data models
│   ├── services/        # Business logic services
│   └── config.py        # Configuration management
├── web/
│   └── app.py           # Streamlit web application
├── data/
│   ├── product_specs/   # Product SKU specifications
│   ├── pricing/         # Pricing tables
│   └── rfps_parsed/     # Parsed RFP documents
├── indexes/             # Vector store indexes
└── requirements.txt     # Python dependencies
```

## 🔧 Configuration

Edit `.env` file:

```env
# LLM Configuration
GOOGLE_API_KEY=your_google_api_key_here
LLM_MODEL=gemini-1.5-pro

# Data Directories
DATA_DIR=./data
INDEXES_DIR=./indexes

# RFP Source URLs
RFP_URLS=https://example.com/rfp1,https://example.com/rfp2
```

## 📊 Sample Data

The project includes sample data:

- **15 Product SKUs**: Various power, control, and instrumentation cables
- **Pricing Tables**: Product and test pricing in INR
- **Demo RFP**: Sample RFP for substation project

## 🧪 Key Components

### Spec Matching Algorithm

The SpecMatch% is computed as:

```
For each specification:
  - Exact match: 100%
  - Numeric within ±10%: 80%
  - Partial match: 50-60%
  - No match: 0%

SpecMatch% = (Sum of matched specs / Total specs) × 100
```

### Pricing Calculation

```
Material Cost = Quantity × Unit Price
Test Cost = Allocated proportionally across items
Total Cost = Material Cost + Allocated Test Cost
```

## 🎨 Tech Stack

- **Orchestration**: LangGraph
- **Retrieval**: LlamaIndex + ChromaDB
- **LLM**: Google Gemini 1.5 Pro
- **Embeddings**: Google Gemini Embeddings
- **Web Framework**: Streamlit
- **Data Validation**: Pydantic
- **Data Processing**: Pandas

## 🔍 Demo Flow (4 minutes)

1. **Introduction** (30s): Problem statement and solution overview
2. **RFP Discovery** (45s): Scan URLs and show filtered RFPs
3. **Agent Workflow** (2m): Run complete workflow with progress tracking
4. **Results Review** (45s): Show spec matching and pricing tables
5. **Wrap-up** (30s): Impact and extensibility

## 📝 Development

### Adding New SKUs

1. Edit `data/product_specs/product_specs.csv`
2. Add pricing in `data/pricing/product_pricing.csv`
3. Rebuild indexes: `python -m src.data_ingestion.build_indexes`

### Adding New RFPs

1. Create JSON file in `data/rfps_parsed/`
2. Follow the RFP model schema from `src/models/rfp_models.py`

## 🐛 Troubleshooting

**Index not found error**:
```bash
python -m src.data_ingestion.build_indexes
```

**Import errors**:
```bash
pip install -r requirements.txt --upgrade
```

**Google API errors**:
- Check your API key in `.env`
- Ensure Gemini API is enabled in Google Cloud Console
- Verify API quota is available

## 📄 License

This project is for demonstration purposes.

## 🤝 Contributing

This is a demo project. For production use, consider:

- Adding authentication
- Implementing proper error handling
- Adding unit tests
- Setting up CI/CD
- Deploying to cloud platform

## 📧 Contact

For questions or feedback, please contact the development team.

---

**Built with ❤️ using LangGraph, LlamaIndex, and Google Gemini**
