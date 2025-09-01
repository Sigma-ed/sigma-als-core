# sigma-als-core
 Django structure showing multi-sector architecture
# Sigma-ALS Core Backend

## 🚀 Multi-Sector AI Learning Platform for Africa

### Overview
Django REST API powering AI-assisted learning across Mathematics, Agricultural Training, and TVET education in African contexts. Built specifically for LMIC constraints with offline-first architecture and teacher quality oversight.

### 🌍 Pilot Validation Results
- **Uganda Mathematics:** 78% engagement, 92% teacher approval
- **Uganda Agriculture:** 85% accuracy, 95% offline success  
- **South Africa TVET:** 65% time savings, 87% content approval
- **Cross-sector average:** 89% success rate

### Architecture Highlights
- **Multi-Tenant Design:** Single backend serving three educational sectors efficiently
- **Hybrid AI System:** Rule-based reliability + GPT-3.5 flexibility for contextual support
- **Offline-First:** SQLite synchronization enabling rural deployment (94% sync success)
- **Teacher Oversight:** Quality control ensuring cultural appropriateness (85-92% approval rates)
- **Mobile-Optimized:** API designed for low-bandwidth, high-latency African networks

## Quick Start

### Prerequisites
- **Python 3.8+** 
- **PostgreSQL 12+** (for production) or SQLite (for development)
- **Redis 6+** for caching and session management
- **OpenAI API key** for AI integration

### Development Setup
```bash
# Clone repository
git clone https://github.com/SigmaALS-Africa/sigma-als-core.git
cd sigma-als-core

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment configuration
cp .env.example .env
# Edit .env with your settings (database, API keys, etc.)

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Load demo data (optional)
python manage.py loaddata fixtures/demo_data.json

# Start development server
python manage.py runserver
