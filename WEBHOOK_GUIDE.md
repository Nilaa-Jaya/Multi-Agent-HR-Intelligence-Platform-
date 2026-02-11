# Multi-Agent HR Intelligence Platform - Webhook Integration Guide

Complete guide for integrating with Multi-Agent HR Intelligence Platform using webhooks.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Event Types](#event-types)
4. [Authentication & Security](#authentication--security)
5. [Payload Format](#payload-format)
6. [Signature Verification](#signature-verification)
7. [Testing Webhooks](#testing-webhooks)
8. [Retry Behavior](#retry-behavior)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Code Examples](#code-examples)

---

## Overview

Webhooks allow you to receive real-time notifications when events occur in Multi-Agent HR Intelligence Platform. Instead of polling for updates, your application will receive HTTP POST requests to a URL you specify.

**Use Cases:**
- Notify your team when queries are escalated
- Track query resolution metrics
- Integrate with CRM systems
- Trigger automated workflows
- Monitor customer feedback in real-time

---

## Quick Start

### 1. Register Your Webhook

```bash
curl -X POST https://your-api.com/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-domain.com/webhook/smartsupport",
    "events": ["query.created", "query.escalated"]
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://your-domain.com/webhook/smartsupport",
  "events": ["query.created", "query.escalated"],
  "secret_key": "wsk_live_abc123def456...",
  "is_active": true,
  "delivery_count": 0,
  "failure_count": 0,
  "created_at": "2024-11-24T12:00:00Z",
  "updated_at": "2024-11-24T12:00:00Z"
}
```

**IMPORTANT:** Save the `secret_key` - you'll need it to verify webhook signatures!

### 2. Implement Your Webhook Endpoint

Your endpoint should:
- Accept HTTP POST requests
- Respond with 2xx status code (200-299)
- Verify the signature (recommended)
- Process the event asynchronously

### 3. Test Your Webhook

```bash
curl -X POST https://your-api.com/api/v1/webhooks/{webhook_id}/test
```

---

## Event Types

Multi-Agent HR Intelligence Platform supports the following event types:

### `query.created`
Triggered when a new customer query is received.

**Use Case:** Track all incoming queries, update dashboards

**Payload Example:**
```json
{
  "event": "query.created",
  "timestamp": "2024-11-24T12:00:00Z",
  "webhook_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "query_id": "conv_abc123",
    "user_id": "user_456",
    "category": "Technical",
    "sentiment": "Negative",
    "priority": 7,
    "query": "My application keeps crashing when I try to export data"
  }
}
```

---

### `query.resolved`
Triggered when a query is successfully resolved.

**Use Case:** Track resolution times, measure agent performance

**Payload Example:**
```json
{
  "event": "query.resolved",
  "timestamp": "2024-11-24T12:05:30Z",
  "webhook_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "query_id": "conv_abc123",
    "user_id": "user_456",
    "category": "Technical",
    "resolution_time_seconds": 330.5,
    "response": "The issue was caused by insufficient memory..."
  }
}
```

---

### `query.escalated`
Triggered when a query is escalated to human support.

**Use Case:** Alert support team, create tickets in your system

**Payload Example:**
```json
{
  "event": "query.escalated",
  "timestamp": "2024-11-24T12:02:15Z",
  "webhook_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "query_id": "conv_abc123",
    "user_id": "user_456",
    "category": "Billing",
    "sentiment": "Angry",
    "priority": 9,
    "escalation_reason": "Billing dispute - requires manual review",
    "query": "I was charged twice for the same subscription"
  }
}
```

---

### `feedback.received`
Triggered when customer provides feedback on AI response.

**Use Case:** Monitor satisfaction, improve AI responses

**Payload Example:**
```json
{
  "event": "feedback.received",
  "timestamp": "2024-11-24T12:10:00Z",
  "webhook_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "query_id": "conv_abc123",
    "user_id": "user_456",
    "rating": 4,
    "feedback_text": "Helpful, but could be more detailed",
    "category": "Technical"
  }
}
```

---

## Authentication & Security

All webhook deliveries include these headers for verification:

| Header | Description | Example |
|--------|-------------|---------|
| `X-Webhook-Signature` | HMAC-SHA256 signature | `a1b2c3d4e5f6...` |
| `X-Webhook-Timestamp` | UTC timestamp | `2024-11-24T12:00:00Z` |
| `X-Webhook-ID` | Your webhook ID | `550e8400-e29b...` |

### Why Verify Signatures?

- Confirms the webhook came from Multi-Agent HR Intelligence Platform
- Prevents replay attacks
- Ensures payload wasn't tampered with

---

## Payload Format

All webhooks follow this structure:

```json
{
  "event": "event.type",
  "timestamp": "2024-11-24T12:00:00Z",
  "webhook_id": "your-webhook-id",
  "data": {
    // Event-specific data
  }
}
```

**Fields:**
- `event` (string): Event type identifier
- `timestamp` (string): UTC timestamp in ISO 8601 format
- `webhook_id` (string): Your webhook UUID
- `data` (object): Event-specific payload

---

## Signature Verification

### How It Works

1. Multi-Agent HR Intelligence Platform generates HMAC-SHA256 hash of the payload using your secret_key
2. Hash is sent in `X-Webhook-Signature` header
3. You generate the same hash and compare

### Python Example

```python
import hmac
import hashlib
import json

def verify_webhook_signature(payload: dict, signature: str, secret_key: str) -> bool:
    """Verify webhook signature"""
    # Convert payload to JSON string (same format as sender)
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))

    # Generate expected signature
    expected_signature = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=payload_str.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    # Compare signatures (timing-safe)
    return hmac.compare_digest(signature, expected_signature)

# Usage
@app.post("/webhook/smartsupport")
async def handle_webhook(request: Request):
    # Get signature from headers
    signature = request.headers.get("X-Webhook-Signature")

    # Get payload
    payload = await request.json()

    # Verify signature
    if not verify_webhook_signature(payload, signature, YOUR_SECRET_KEY):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Process webhook
    await process_webhook(payload)

    return {"status": "received"}
```

### Node.js Example

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secretKey) {
    // Convert payload to JSON string
    const payloadStr = JSON.stringify(payload);

    // Generate expected signature
    const expectedSignature = crypto
        .createHmac('sha256', secretKey)
        .update(payloadStr)
        .digest('hex');

    // Compare signatures (timing-safe)
    return crypto.timingSafeEqual(
        Buffer.from(signature),
        Buffer.from(expectedSignature)
    );
}

// Express.js endpoint
app.post('/webhook/smartsupport', async (req, res) => {
    const signature = req.headers['x-webhook-signature'];
    const payload = req.body;

    if (!verifyWebhookSignature(payload, signature, process.env.SECRET_KEY)) {
        return res.status(401).json({ error: 'Invalid signature' });
    }

    // Process webhook
    await processWebhook(payload);

    res.status(200).json({ status: 'received' });
});
```

---

## Testing Webhooks

### Method 1: Use webhook.site

1. Go to https://webhook.site/
2. Copy your unique URL
3. Register webhook:
```bash
curl -X POST https://your-api.com/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://webhook.site/your-unique-id",
    "events": ["query.created"]
  }'
```
4. Trigger an event
5. View the payload on webhook.site

### Method 2: Test Endpoint

```bash
curl -X POST https://your-api.com/api/v1/webhooks/{webhook_id}/test
```

**Response:**
```json
{
  "success": true,
  "status_code": 200,
  "response_time_ms": 145.3,
  "error": null
}
```

### Method 3: Local Testing with ngrok

```bash
# Start ngrok
ngrok http 3000

# Use ngrok URL for webhook
curl -X POST https://your-api.com/api/v1/webhooks \
  -d '{
    "url": "https://abc123.ngrok.io/webhook",
    "events": ["query.created"]
  }'
```

---

## Retry Behavior

### Automatic Retries

Multi-Agent HR Intelligence Platform automatically retries failed webhook deliveries:

- **Attempts:** 3 total attempts
- **Backoff:** Exponential (1s, 2s, 4s)
- **Timeout:** 10 seconds per attempt
- **Success:** 2xx status codes (200-299)
- **No Retry:** 4xx status codes (client errors)
- **Retry:** 5xx status codes (server errors) and timeouts

### Example Timeline

```
Attempt 1: Immediate → Fails (500)
  ↓ Wait 1 second
Attempt 2: 1s later → Fails (timeout)
  ↓ Wait 2 seconds
Attempt 3: 3s later → Fails (503)
  ↓ Marked as failed
```

### Checking Delivery Logs

```bash
curl https://your-api.com/api/v1/webhooks/{webhook_id}/deliveries
```

---

## Best Practices

### 1. Respond Quickly

```python
# [DONE] Good: Return 200 immediately, process async
@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    background_tasks.add_task(process_webhook, payload)
    return {"status": "received"}

# [FAIL] Bad: Process synchronously
@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    await slow_processing(payload)  # This delays the response!
    return {"status": "received"}
```

### 2. Always Verify Signatures

```python
# [DONE] Good: Verify before processing
if not verify_signature(payload, signature, secret_key):
    raise HTTPException(status_code=401)
process_webhook(payload)

# [FAIL] Bad: Trust without verification
process_webhook(payload)  # Security risk!
```

### 3. Handle Idempotency

```python
# [DONE] Good: Check for duplicates
if already_processed(payload["data"]["query_id"]):
    return {"status": "already processed"}
process_webhook(payload)

# [FAIL] Bad: Process every delivery
process_webhook(payload)  # May process duplicates!
```

### 4. Log Everything

```python
# [DONE] Good: Comprehensive logging
logger.info(f"Webhook received: {payload['event']}")
logger.info(f"Query ID: {payload['data']['query_id']}")
logger.info(f"Timestamp: {payload['timestamp']}")
```

### 5. Use HTTPS

```python
# [DONE] Good: Secure endpoint
url = "https://your-domain.com/webhook"

# [FAIL] Bad: Insecure endpoint (production)
url = "http://your-domain.com/webhook"  # Not secure!
```

---

## Troubleshooting

### Webhook Not Receiving Events

**Check:**
1. Is webhook `is_active: true`?
```bash
curl https://your-api.com/api/v1/webhooks/{webhook_id}
```

2. Are you subscribed to the event?
```json
{
  "events": ["query.created", "query.escalated"]
}
```

3. Is your endpoint accessible?
```bash
curl -X POST https://your-domain.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

---

### Signature Verification Fails

**Common Issues:**
1. **Payload modification:** Don't modify payload before verifying
2. **Wrong secret key:** Use the key from webhook creation response
3. **JSON formatting:** Ensure consistent JSON formatting

```python
# Correct way:
raw_body = await request.body()
payload = json.loads(raw_body)
verify_signature(payload, signature, secret_key)
```

---

### High Failure Rate

**Check delivery logs:**
```bash
curl https://your-api.com/api/v1/webhooks/{webhook_id}/deliveries
```

**Common causes:**
- Endpoint timeouts (>10s)
- Server errors (5xx)
- SSL certificate issues
- Firewall blocking requests

---

## Code Examples

### Full Flask Example

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import json

app = Flask(__name__)
SECRET_KEY = "your_secret_key_here"

def verify_signature(payload, signature):
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    expected = hmac.new(
        SECRET_KEY.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

@app.route('/webhook/smartsupport', methods=['POST'])
def handle_webhook():
    # Get signature
    signature = request.headers.get('X-Webhook-Signature')
    if not signature:
        return jsonify({'error': 'Missing signature'}), 401

    # Get payload
    payload = request.get_json()

    # Verify signature
    if not verify_signature(payload, signature):
        return jsonify({'error': 'Invalid signature'}), 401

    # Process based on event type
    event_type = payload['event']

    if event_type == 'query.created':
        handle_query_created(payload['data'])
    elif event_type == 'query.escalated':
        handle_query_escalated(payload['data'])
    elif event_type == 'feedback.received':
        handle_feedback(payload['data'])

    return jsonify({'status': 'received'}), 200

def handle_query_created(data):
    print(f"New query: {data['query_id']}")
    # Your logic here

def handle_query_escalated(data):
    print(f"Escalated: {data['query_id']}")
    # Alert your team

def handle_feedback(data):
    print(f"Feedback: {data['rating']}/5")
    # Log to analytics

if __name__ == '__main__':
    app.run(port=3000)
```

### Full Express.js Example

```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();
app.use(express.json());

const SECRET_KEY = process.env.SECRET_KEY;

function verifySignature(payload, signature) {
    const payloadStr = JSON.stringify(payload);
    const expected = crypto
        .createHmac('sha256', SECRET_KEY)
        .update(payloadStr)
        .digest('hex');

    return crypto.timingSafeEqual(
        Buffer.from(signature),
        Buffer.from(expected)
    );
}

app.post('/webhook/smartsupport', async (req, res) => {
    const signature = req.headers['x-webhook-signature'];
    const payload = req.body;

    if (!verifySignature(payload, signature)) {
        return res.status(401).json({ error: 'Invalid signature' });
    }

    const { event, data } = payload;

    switch (event) {
        case 'query.created':
            await handleQueryCreated(data);
            break;
        case 'query.escalated':
            await handleQueryEscalated(data);
            break;
        case 'feedback.received':
            await handleFeedback(data);
            break;
    }

    res.json({ status: 'received' });
});

async function handleQueryCreated(data) {
    console.log(`New query: ${data.query_id}`);
}

async function handleQueryEscalated(data) {
    console.log(`Escalated: ${data.query_id}`);
    // Alert team via Slack, email, etc.
}

async function handleFeedback(data) {
    console.log(`Feedback: ${data.rating}/5`);
}

app.listen(3000, () => {
    console.log('Webhook server running on port 3000');
});
```

---

## API Reference

### Register Webhook
```
POST /api/v1/webhooks
```

### List Webhooks
```
GET /api/v1/webhooks?skip=0&limit=100&is_active=true
```

### Get Webhook
```
GET /api/v1/webhooks/{webhook_id}
```

### Update Webhook
```
PUT /api/v1/webhooks/{webhook_id}
```

### Delete Webhook
```
DELETE /api/v1/webhooks/{webhook_id}
```

### Test Webhook
```
POST /api/v1/webhooks/{webhook_id}/test
```

### Get Delivery Logs
```
GET /api/v1/webhooks/{webhook_id}/deliveries?skip=0&limit=50
```

---

## Support

**Issues?**
- Check troubleshooting section
- Review delivery logs
- Test with webhook.site
- Contact support with webhook ID

**Resources:**
- API Documentation: `/docs`
- GitHub: Repository issues
- Email: support@example.com

---

**Last Updated:** 2024-11-24
**Version:** 1.0.0
**Status:** [DONE] Production Ready
