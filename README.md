# 📝 AS Proposal Generator

[![Live Demo](https://img.shields.io/badge/🌐%20Live-AS%20Proposal%20Generator-brightgreen)](https://as-proposal-generator-app-566552386634.us-central1.run.app/)

## 📌 Overview

**AS Proposal Generator** is an automated proposal generation system designed to streamline the process of creating well-structured, professional proposals efficiently. It uses AI-powered formatting and content suggestions to reduce manual effort.

---

## 🚀 Features

- 📄 **Automated Proposal Drafting** – Generates structured proposals based on user inputs.
- 🧩 **Customizable Templates** – Supports predefined and user-defined templates for different use cases.
- ✨ **Efficient Formatting** – Ensures professional structure and readability.
- 🧠 **Content Optimization** – Offers AI-based suggestions to enhance clarity and tone.

---

## 🛠️ Installation

To run the project locally:

```bash
git clone https://github.com/Aswinthmani2003/AS-Proposal_Generator.git
cd AS-Proposal_Generator
```

Create and activate a virtual environment:

- On **macOS/Linux**:

```bash
python3 -m venv venv
source venv/bin/activate
```

- On **Windows**:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 💡 Usage

1. **Run the app**:
   ```bash
   python main.py
   ```

2. **Input Proposal Details**:
   Provide client/project information, goals, and requirements.

3. **Select Template**:
   Choose from pre-built templates or let the AI assist you.

4. **Generate Proposal**:
   The tool generates a complete, structured proposal document.

5. **Export**:
   Export your final proposal as a PDF or Word document.

---

## 🐳 Docker Deployment (Optional)

```bash
docker build -t as-proposal-generator .
docker run -p 5000:5000 as-proposal-generator
```

Open your browser at: [http://localhost:5000](http://localhost:5000)

---

## 📁 Proposal Types Supported

- Project-based Proposals
- Client Onboarding Proposals
- Service Offering Proposals
- Custom Template-Based Proposals

---

## 🤝 Contributing

1. Fork the repo
2. Create a new branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -m "Add new feature"`)
4. Push to the branch (`git push origin feature-name`)
5. Open a pull request

---

## 📞 Contact

- 📧 Email: aswinthmani10@gmail.com  
- 🐙 GitHub: [@Aswinthmani2003](https://github.com/Aswinthmani2003)

---

## ☁️ Deployment

The app is live and deployed on **Google Cloud Platform**:

🌐 **Live Demo**: [https://as-proposal-generator-app-566552386634.us-central1.run.app/](https://as-proposal-generator-app-566552386634.us-central1.run.app/)

To deploy it yourself using GCP App Engine:

**`app.yaml`**:

```yaml
runtime: python310
entrypoint: streamlit run main.py --server.port=8080 --server.enableCORS=false

instance_class: F2
automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 1
  max_instances: 2
```

Then run:

```bash
gcloud app deploy
```

---

> Crafted with ❤️ to simplify and accelerate proposal creation.
