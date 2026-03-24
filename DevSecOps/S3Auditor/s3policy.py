import boto3
import json
import datetime

def audit_s3_buckets(bucket_name: str = None, region_filter: str = None):
    print("[+] Thought: Starting audit of S3 buckets")
    s3 = boto3.client('s3')
    results = []

    try:
        all_buckets = s3.list_buckets()['Buckets']
        buckets = [b for b in all_buckets if(not bucket_name or b['Name'] == bucket_name)]
        for bucket in buckets:
            name = bucket['Name']
            region = s3.get_bucket_location(Bucket=name).get('LocationConstraint') or 'us-east-1'
            if region_filter and region != region_filter:
                print(f"[-] Skipping {name}, not in region {region_filter}")
                continue
            print(f"> Auditing bucket: {name}")
            encryption = versioning = public_access = lifecycle = None
            try: 
                encryption = s3.get_bucket_encryption(Bucket=name)
            except: pass

            try: 
                versioning = s3.get_bucket_versioning(Bucket=name)
            except: pass

            try: 
                acl = s3.get_bucket_acl(Bucket=name)
                public_access = any(grant['Grantee'].get('URI','').endswith('AllUsers') or
                                    grant['Grantee'].get('URI','').endswith('AuthenticatedUsers')
                                    for grant in acl['Grants'])
            except: pass
            try: 
                lifecycle = s3.get_bucket_lifecycle_configuration(Bucket=name)
            except: pass

            if public_access:
                print(f"Warning: {name} is public!")
            if not encryption:
                print(f"Warning: {name} is not encrypted!")
            if not versioning or versioning.get('Status') != 'Enabled':
                print(f"Warning: {name} versioning is not enabled!")
            if not lifecycle or lifecycle.get('Rules'):
                print(f"Warning: {name} missing lifecycle policy!")

            results.append({
                "bucket_name": name,
                "region": region,
                "is_public": public_access,
                "is_encrypted": 'SeverSideEncryption Configuration' in (encryption or {}),
                "versioning_enabled": versioning.get('Status') == 'Enabled' if versioning else False,
                "has_lifecycle_policy": bool(lifecycle and lifecycle.get('Rules'))
            })           
    
    except Exception as e:
        return {"error": str(e)}
    
    filename = f"s3_audit_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return {
        "summary": f"Audited {len(results)} buckets",
        "buckets": results
    }
