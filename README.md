# ChatAI: SaaS Chatbot-as-a-Service Platform

## Overview
ChatAI is a SaaS platform that enables businesses to create, customize, and embed AI-powered chatbots on their websites with minimal setup. Each business can manage its own chatbots, settings, and prompts, and easily integrate the chatbot widget using a simple JavaScript API.

## Features
- **Multi-Tenant Support:** Each business (tenant) has isolated chatbot configurations and data.
- **User Authentication:** Secure signup and login for business users.
- **Chatbot Management:** Create, update, and manage multiple chatbots per business.
- **Custom Prompts & Settings:** Businesses can define chatbot behavior and appearance.
- **Embeddable Widget:** Simple JS API to embed the chatbot on any website.
- **RESTful API:** FastAPI-powered backend for all operations.

## Project Structure
```
app/
  main.py
  api/
    v1/
      endpoints/
        auth.py
        chatbot.py
        tenant.py
  core/
    config.py
    security.py
  models/
    user.py
    tenant.py
    chatbot.py
  schemas/
    user.py
    tenant.py
    chatbot.py
  services/
    chatbot_service.py
  static/
    js/
      embed.js
  templates/
  tests/
requirements.txt
README.md
```

## Getting Started
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd ChatAI
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the app:**
   ```bash
   uvicorn app.main:app --reload
   ```

## Roadmap
- [x] Project structure & initialization
- [ ] User authentication (JWT)
- [ ] Multi-tenant support
- [ ] Chatbot CRUD endpoints
- [ ] Embeddable JS widget
- [ ] Dashboard UI (optional)
- [ ] Deployment & docs

## License
MIT 