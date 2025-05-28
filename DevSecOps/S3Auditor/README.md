# 🛡️ S3 Security Audit AI Agent

This AI-powered Python tool audits your AWS S3 buckets for security misconfigurations using **GPT-4o**, **boto3**, **Jinja2**, and **pdfkit**.  
It generates:

- ✅ A detailed **PDF report**
- ✅ A **JSON** file with audit results
- ✅ 🧠 Smart reasoning from GPT on what to audit, all triggered via natural language prompts

---

## 🔍 What It Audits

- 🌐 Public access permissions
- 🔐 Server-side encryption
- ♻️ Lifecycle policies
- 📦 Versioning configuration

---

## ⚙️ Setup

### 1. Clone this repo
git clone [https://github.com/yourusername/s3-audit-agent.git](https://github.com/UnpredictablePrashant/AIAgent.git)


```bash
git clone [https://github.com/UnpredictablePrashant/AIAgent.git](https://github.com/UnpredictablePrashant/AIAgent.git)
cd DevSecOps/s3-audit-agent
```

### 2. Install dependencies

```bash
pip install boto3 jinja2 pdfkit openai
```

### 3. Install `wkhtmltopdf` (required for PDF generation)

- **Windows/macOS**: [Download from here](https://wkhtmltopdf.org/downloads.html)
- **Ubuntu/Debian**:
  ```bash
  sudo apt install wkhtmltopdf
  ```

---

## 🔑 API Key & AWS Setup

### 1. Set up your OpenAI API Key

You can set your key in two ways:

#### Option A: Use `.env` file

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
```

Then load it in Python using `dotenv`:

```bash
pip install python-dotenv
```

In your script:

```python
from dotenv import load_dotenv
load_dotenv()
```

#### Option B: Set it as an environment variable

```bash
export OPENAI_API_KEY=sk-...
```

Or on Windows:

```cmd
set OPENAI_API_KEY=sk-...
```

---

### 2. Configure AWS Credentials

Make sure your AWS credentials are configured via one of these:

#### Option A: Use AWS CLI

```bash
aws configure
```

Provide:

- Access Key ID
- Secret Access Key
- Default Region
- Output format

These are saved under `~/.aws/credentials`.

#### Option B: Environment variables

```bash
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=abc123...
```

---

## 🧠 Run the Agent

```bash
python devopsAgent.py
```

You’ll see:

```
💬 Ask your DevOps AI Agent:
```

Type a prompt like:

```
Audit all S3 buckets in ap-south-1
```

Or:

```
Check security of customer-data-bucket
```

---

## 📄 Output

1. 📝 A PDF report like: `s3_audit_report_20240714_162830.pdf`
2. 📦 A JSON file like: `s3_audit_output_20240714_162830.json`

Both are saved in the current directory.

---

## 📁 Folder Structure

```
s3-audit-agent/
├── devopsAgent.py
├── templates/
│   └── s3_report.html
├── .env (optional)
├── requirements.txt (optional)
```

---

## 🧩 Prompt-To-Action Mapping

| Prompt Example                                 | GPT Action              |
|-----------------------------------------------|-------------------------|
| "Audit all buckets"                            | Calls `audit_s3_buckets()` |
| "Check bucket named logs-prod in us-west-2"    | Calls with args `bucket_name`, `region_filter` |
| "Show security of S3 buckets in ap-south-1"    | Region filter applied   |

---

## 🧠 How It Works

- **OpenAI GPT-4o** reads your prompt and decides which function to call
- **Boto3** scans your S3 buckets
- **Jinja2 + pdfkit** render and export a styled PDF
- JSON result is saved for programmatic use

---

## ✨ Roadmap

- 📬 Email/Slack report delivery
- 🔄 Schedule as a daily/weekly job
- 🌍 Web dashboard view
- 🔐 IAM policy scanner

---

## 👨‍💻 Author

**Prashant Kumar Dey**  
Cloud | AI | Cybersecurity  
📬 [LinkedIn](https://www.linkedin.com/in/prashantkumardey)

---

## 🛡️ License

MIT License
