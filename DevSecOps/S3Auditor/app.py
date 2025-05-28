from openai import OpenAI
import boto3
import json
import os
import re

from jinja2 import Environment, FileSystemLoader
import pdfkit
import datetime


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "sk-.."))

tools = [

    {
        "type": "function",
        "function": {
            "name": "audit_s3_buckets",
            "description": "Audit S3 buckets for security risks. You can audit all or specify a bucket name or region.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bucket_name": {"type": "string", "description": "Optional specific bucket name to audit"},
                    "region_filter": {"type": "string", "description": "Optional AWS region to filter buckets"}
                }
            }
        }
    }

]

def audit_s3_buckets(bucket_name: str = None, region_filter: str = None):
    print("🧠 Thought: Starting audit of S3 buckets...")
    s3 = boto3.client('s3')
    results = []

    try:
        all_buckets = s3.list_buckets()['Buckets']
        buckets = [b for b in all_buckets if (not bucket_name or b['Name'] == bucket_name)]

        for bucket in buckets:
            name = bucket['Name']
            region = s3.get_bucket_location(Bucket=name).get('LocationConstraint') or 'us-east-1'

            if region_filter and region != region_filter:
                print(f"🧠 Skipping {name}, not in region {region_filter}")
                continue

            print(f"🧠 Auditing bucket: {name}")
            encryption = versioning = public_access = lifecycle = None

            try:
                encryption = s3.get_bucket_encryption(Bucket=name)
            except: pass

            try:
                versioning = s3.get_bucket_versioning(Bucket=name)
            except: pass

            try:
                acl = s3.get_bucket_acl(Bucket=name)
                public_access = any(grant['Grantee'].get('URI', '').endswith('AllUsers') or
                                    grant['Grantee'].get('URI', '').endswith('AuthenticatedUsers')
                                    for grant in acl['Grants'])
            except: pass

            try:
                lifecycle = s3.get_bucket_lifecycle_configuration(Bucket=name)
            except: pass

            # Print warnings
            if public_access: print(f"⚠️ Warning: {name} is public!")
            if not encryption: print(f"⚠️ Warning: {name} is not encrypted!")
            if not versioning or versioning.get('Status') != 'Enabled': print(f"⚠️ Warning: {name} versioning not enabled!")
            if not lifecycle or not lifecycle.get('Rules'): print(f"⚠️ Warning: {name} missing lifecycle policy!")

            results.append({
                "bucket_name": name,
                "region": region,
                "is_public": public_access,
                "is_encrypted": 'ServerSideEncryptionConfiguration' in (encryption or {}),
                "versioning_enabled": versioning.get('Status') == 'Enabled' if versioning else False,
                "has_lifecycle_policy": bool(lifecycle and lifecycle.get('Rules'))
            })
    except Exception as e:
        return {"error": str(e)}
     # 🧠 Generate PDF after collecting all audit results
    filename = f"s3_audit_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = generate_s3_pdf_report(results, output_path=filename)

    json_filename = f"s3_audit_output_{timestamp}.json"

    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        print(f"✅ JSON data saved: {json_filename}")
    return {
        "summary": f"Audited {len(results)} buckets.",
        "buckets": results
    }

def generate_s3_pdf_report(buckets: list, output_path: str = "s3_audit_report.pdf"):
    print("🧠 Thought: Generating PDF with pdfkit...")

    # Load HTML template
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("s3_report.html")
    html_out = template.render(buckets=buckets)

    # Write PDF
    options = {
        'page-size': 'A4',
        'encoding': 'UTF-8',
        'enable-local-file-access': ''
    }

    try:
        pdfkit.from_string(html_out, output_path, options=options)
        print(f"✅ PDF report generated at: {output_path}")
        return output_path
    except Exception as e:
        print("❌ Error generating PDF:", str(e))
        return None


handlers = {
    "fix_iam_policy": fix_iam_policy,
    "optimize_dockerfile": optimize_dockerfile,
    "audit_s3_buckets": audit_s3_buckets
}

def run_agent(user_prompt: str):
    print("🧠 Thought: Asking GPT to analyze user prompt and decide which tool to call...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
            You are an AWS Cloud Security Auditor. Your job is to check AWS S3 buckets for misconfigurations, including:
                - Public access
                - Unencrypted buckets
                - Missing versioning
                - Missing lifecycle policies

            Use the AWS SDK to audit each bucket and return a detailed risk analysis for every bucket found.

            """},
            {"role": "user", "content": user_prompt}
        ],
        tools=tools,
        tool_choice="auto"
    )

    tool_calls = response.choices[0].message.tool_calls

    if tool_calls:
        results = []
        for call in tool_calls:
            function_name = call.function.name
            arguments = json.loads(call.function.arguments)
            if function_name in handlers:
                result = handlers[function_name](**arguments)
                results.append({"function": function_name, "result": result})
            else:
                results.append({"error": f"Function '{function_name}' not implemented."})
        return results
    else:
        return {"response": "🤔 GPT did not call any tool."}

if __name__ == "__main__":
    user_prompt = input("💬 Ask your DevOps AI Agent: ")
    results = run_agent(user_prompt)
    print(json.dumps(results, indent=2))
