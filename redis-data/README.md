# Redis Data Folder

This folder is used for **Redis persistence storage**, specifically for **RDB snapshots**.

## Contents:
- `dump.rdb` → Redis snapshot file that stores database data periodically.
- Any other Redis-generated persistence files.

## Important Notes:
- The `dump.rdb` file contains **Redis in-memory data** and is **automatically created/updated** by Redis.
- This file is **ignored in Git** to prevent committing unnecessary data.
- If Redis persistence is enabled (`save` directives in `redis.conf`), this file ensures data is **restored after a restart**.
- If using Docker, this folder is typically **mounted to `/data`** inside the container.
- To manually trigger a snapshot, run: redis-cli SAVE
