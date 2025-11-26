# Auto-Healing Pipeline

A RAG-powered pipeline that automatically fixes file naming and project structure issues before deploying to Netlify.

## Features

- 🔍 **Project Analysis**: Scans for invalid filenames and structure issues
- 🛠️ **Auto-Healing**: Fixes issues using RAG-powered suggestions
- 📝 **GitHub Integration**: Automatically commits fixes
- 🚀 **Netlify Deployment**: Deploys healed project automatically

## Setup

1. **Clone and setup**:
```bash
git clone <your-repo>
cd auto-healing-pipeline
pip install -r requirements.txt