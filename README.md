# cloudwatch-to-stdf
Terraform module to standup a lambda that converts a random cloudwatch output to the Standard Format

#### STDF v2

```json
{
    "payload": {
        "title": "Security Alert",
        "description": "Somebody is trying to hack you",
        "raw_data": "by applying bad things to your infra"
    },
    "meta": {
        "timestamp": UNIX_miliseconds,
        "source": {
          "provider": "AWS",
          "account_id": "906911110000",
          "region": "us-east-9000",
          "service": "CloudWatch",
          "event_id": "00000000-0000-0000-000000000000" (optional),
          "app_name": "Jamf"
        },
        "urls": [
            {
            "text": "View policy",
            "url": "https://examlpe.com"
            },
        ...
    ]
},
"stdf_version": 2,
}
```
