from openai import OpenAI
import json
from s3policy import audit_s3_buckets

client = OpenAI(api_key='')


tools = [{
    "type": "function",
    "function": {
        "name": "audit_s3_buckets",
        "description": "Audit s3 buckets for security risks. You can audit all or specify a bucket name or region.",
        "parameters": {
            "type": "object",
            "properties": {
                "bucket_name": {"type": "string", "description": "Optional specific bucket name to audit"},
                "region_filter": {"type": "string", "description": "Optional specific AWS region to filter and audit buckets"}
            }
            
        }
    }
}]

handlers = {
    "audit_s3_buckets": audit_s3_buckets
}

def run_agent(user_prompt: str):
    print("[+] Thoughts: Asking GPT to analyse user prompt and decide which tool to call...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
            You are an AWS Cloud Security Auditor and the docker expert. Your job is to check AWS S3 buckets for misconfigurations, including:
             - Public Access
             - Unencrypted Buckets
             - Missing Versioning
             - Missing lifecycle Policies
            Use the AWS SDK to audit each bucket and return a detailed risk analysis for every bucket found.
            """},
            {"role": "user", "content": user_prompt}
        ],
        tools=tools,
        tool_choice="auto"
    )
    # print(response)
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
        return {"response": "[!] GPT did not call any tool"}

if __name__ == "__main__":
    user_prompt = input("?? Ask your DevOps AI Agent for Auditing S3: ")
    results = run_agent(user_prompt)
    print(json.dumps(results, indent=2))
