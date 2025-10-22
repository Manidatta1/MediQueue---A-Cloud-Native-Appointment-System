# RabbitMQ Topology (Worker view)

- **Exchange:** `events`
  - **Type:** `topic`
  - **Durable:** true
- **Routing keys:**
  - `appointments.created`
  - `appointments.cancelled` (later)
- **Worker queue:** `worker.notifications` (durable)
  - Bindings:
    - `events` ← `appointments.created`
    - `events` ← `appointments.cancelled` (later)
- **QoS:** prefetch=8
- **Acks:** manual ack on success; nack (no requeue) on malformed payloads
- **DLQ:** (optional) `dlx.events` for malformed messages
