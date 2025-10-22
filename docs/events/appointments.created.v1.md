# Event: `appointment_created` (v1)

**Purpose:** trigger patient reminders for an upcoming appointment.

**Routing**
- Exchange: `events` (type: `topic`)
- Routing key: `appointments.created`

**Delivery & Time**
- At-least-once delivery (idempotency required).
- All timestamps in **UTC** ISO-8601 (`YYYY-MM-DDTHH:MM:SSZ`).

**Fields**
| Path | Type | Req | Notes |
|---|---|---|---|
| event | string | ✔ | `appointment_created` |
| version | integer | ✔ | `1` |
| id | uuid | ✔ | Unique event ID for dedupe |
| occurred_at | string(ISO-8601) | ✔ | UTC |
| appointment.id | uuid | ✔ | Appointment PK |
| appointment.doctor_id | integer | ✔ | |
| appointment.patient_id | integer | ✔ | |
| appointment.start_ts | string(ISO-8601) | ✔ | UTC |
| appointment.end_ts | string(ISO-8601) | ✔ | UTC |
| appointment.channel_hint[] | array<string> | optional | default `["sms","email"]` |
| meta.request_id | string | optional | for log correlation |

**Idempotency**
- Consumer should ignore duplicates by `event.id` (or treat schedule as upsert).

**Example**
```json
{
  "event": "appointment_created",
  "version": 1,
  "id": "5b8e3f2e-4e2f-4d5f-9b55-3a2f6b2c9d30",
  "occurred_at": "2025-10-22T17:05:00Z",
  "appointment": {
    "id": "a1b2c3d4-e5f6-7788-9900-aabbccddeeff",
    "doctor_id": 101,
    "patient_id": 501,
    "start_ts": "2025-10-23T10:00:00Z",
    "end_ts": "2025-10-23T10:30:00Z",
    "channel_hint": ["sms", "email"]
  },
  "meta": { "request_id": "req_abc123" }
}
