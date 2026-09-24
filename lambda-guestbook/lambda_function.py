import json
import os
import uuid
import re
from datetime import datetime, timezone
import boto3

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

TABLE_NAME = os.environ.get("TABLE_NAME", "GuestbookMessages")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")  # để trống nếu không dùng SNS

table = dynamodb.Table(TABLE_NAME)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Headers CORS dùng chung cho mọi response
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",  # có thể thay bằng domain WordPress cụ thể để chặt hơn
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST",
}


def _response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body_dict, ensure_ascii=False),
    }


def lambda_handler(event, context):
    # API Gateway gửi request OPTIONS (preflight) trước khi gửi POST thật - phải trả lời OK
    http_method = event.get("httpMethod", "")
    if http_method == "OPTIONS":
        return _response(200, {"message": "ok"})

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"error": "Body không phải JSON hợp lệ"})

    name = (body.get("name") or "").strip()
    email = (body.get("email") or "").strip()
    message = (body.get("message") or "").strip()

    # Validate cơ bản
    if not name or not message:
        return _response(400, {"error": "Thiếu tên hoặc nội dung tin nhắn"})
    if len(name) > 100 or len(message) > 2000:
        return _response(400, {"error": "Tên hoặc nội dung quá dài"})
    if email and not EMAIL_REGEX.match(email):
        return _response(400, {"error": "Email không hợp lệ"})

    item = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "message": message,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }

    try:
        table.put_item(Item=item)
    except Exception as e:
        print(f"DynamoDB put_item error: {e}")
        return _response(500, {"error": "Không thể lưu tin nhắn, vui lòng thử lại sau"})

    # Gửi thông báo qua SNS nếu có cấu hình topic (không bắt buộc)
    if SNS_TOPIC_ARN:
        try:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="Guestbook: Có tin nhắn mới",
                Message=f"Tên: {name}\nEmail: {email or '(không cung cấp)'}\nNội dung: {message}",
            )
        except Exception as e:
            # Không để lỗi SNS làm hỏng cả request - tin nhắn đã lưu DB thành công là quan trọng nhất
            print(f"SNS publish error: {e}")

    return _response(200, {"message": "Gửi tin nhắn thành công!"})
