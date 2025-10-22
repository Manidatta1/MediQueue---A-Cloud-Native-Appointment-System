# Event: `appointment_cancelled` (v1)

**Routing**
- Exchange: `events` (topic)
- Routing key: `appointments.cancelled`

**Fields**
| Path | Type | Req | Notes |
|---|---|---|---|
| event | string | ✔ | `appointment_cancelled` |
| version | integer | ✔ | `1` |
| id | uuid | ✔ | Event ID |
| occurred_at | string(ISO-8601) | ✔ | UTC |
| appointment.id | uuid | ✔ | Appointment PK |

**Behavior**
- Mark all **future** notifications for `appointment.id` as `failed` with reason `cancelled`.