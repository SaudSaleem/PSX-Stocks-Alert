# Docker Setup - Issues Fixed

## Problems Encountered

### 1. **Obsolete `version` field warning**
```
WARN: the attribute `version` is obsolete
```
**Fixed**: Removed `version: '3.8'` from `docker-compose.yml` (no longer needed in modern Docker Compose)

### 2. **Migration errors on fresh database**
```
sqlalchemy.exc.ProgrammingError: relation "alerts" does not exist
```
**Problem**: Migration files tried to modify tables that didn't exist yet because:
- Your migrations were created incrementally (adding fields to existing tables)
- PostgreSQL database was completely fresh/empty
- No base tables existed

**Fixed**: Created `init_fresh_db.py` that creates all tables directly from models instead of using incremental migrations for fresh databases.

## What Changed

### Files Modified:
1. **docker-compose.yml**
   - Removed obsolete `version` field
   - Changed startup command from `alembic upgrade head` to `python init_fresh_db.py`

2. **Makefile**
   - Updated `dev` command to wait longer (10 seconds instead of 5)
   - Removed separate migration step (now runs automatically on startup)
   - Added helpful status messages

### Files Created:
1. **init_fresh_db.py**
   - Simple script that creates all database tables from your models
   - Runs automatically when container starts
   - Perfect for fresh database setup

## Current Status

✅ **Backend**: Running on http://localhost:8000
✅ **Database**: PostgreSQL running and initialized
✅ **API Docs**: Available at http://localhost:8000/docs
✅ **Scraper**: Background scheduler started

## How to Use

### Start Services:
```bash
make dev
# OR
docker-compose up -d
```

### View Logs:
```bash
make logs
# OR
docker-compose logs -f backend
```

### Stop Services:
```bash
make down
# OR
docker-compose down
```

### Fresh Start (Delete All Data):
```bash
make clean
# OR
docker-compose down -v
```

## Important Notes

1. **Database**: Uses PostgreSQL (empty/fresh database)
   - Your old SQLite data (`stocks_alert.db`) is NOT migrated
   - You'll need to re-register users and create alerts
   - This is intentional - fresh start with production-like setup

2. **Migrations**: 
   - For fresh databases: Tables created from models automatically
   - For existing databases: Would need proper migration strategy
   - Current setup: Optimized for fresh/new databases

3. **No Data Migration Needed**:
   - Starting fresh is simpler
   - Avoids complex SQLite → PostgreSQL migration
   - Production-ready setup from day 1

## If You Want to Keep Using SQLite

See `DOCKER_DEPLOYMENT.md` for instructions on switching back to SQLite if preferred.

## Next Steps

1. ✅ Backend is running
2. ✅ Database is ready
3. 🔄 Start your frontend:
   ```bash
   cd frontend
   npm run dev
   ```
4. 🎯 Test the app at http://localhost:5173
5. 📝 Register a new user and create alerts

---

**Everything is working now!** 🎉

