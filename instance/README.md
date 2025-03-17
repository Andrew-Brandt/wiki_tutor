# Instance Folder

This folder is used for storing application-specific data that should not be committed to version control.

## Contents:
- `app.db` → SQLite database file (ignored in Git)
- Any other runtime-generated data

## Important Notes:
- The database file (`app.db`) is **ignored in Git** to prevent local data conflicts.
- If you need a fresh database, it will be created automatically when running the application.
- This folder should remain present to ensure proper application functionality.
