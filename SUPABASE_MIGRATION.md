# Supabase Migration Guide

This guide explains how to use Supabase as your database instead of the local Docker PostgreSQL.

## What Changed

✅ **Removed**: Local PostgreSQL Docker container
✅ **Updated**: Database connection to use Supabase
✅ **Benefits**: 
- No need to manage database infrastructure
- Automatic backups
- Better scalability
- Built-in database UI for monitoring

## Setup Instructions

### 1. Get Your Supabase Connection String

From your Supabase Dashboard:
1. Go to **Settings** > **Database**
2. Find the **Connection String** section
3. Select **URI** tab
4. Copy the connection string (it looks like):
   ```
   postgresql://postgres:[YOUR_PASSWORD]@db.kizbfvvpxwaabhzulaxe.supabase.co:5432/postgres
   ```

### 2. Configure Your Environment

#### Option A: Using .env file (Local Development)

Create a `.env` file in the project root:

```bash
# Replace [YOUR_PASSWORD] with your actual Supabase database password
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.kizbfvvpxwaabhzulaxe.supabase.co:5432/postgres

# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=True

# JWT Secret Key
SECRET_KEY=your-secret-key-change-in-production

# Twilio Configuration
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

#### Option B: Using Docker Compose

The `docker-compose.yml` now reads from environment variables. Make sure to set `DATABASE_URL` in your `.env` file as shown above.

### 3. Run Database Migrations

Run Alembic migrations to create tables in your Supabase database:

```bash
# If using virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run migrations
alembic upgrade head
```

Or with Docker:

```bash
docker-compose up
```

The migrations will run automatically when the container starts.

### 4. Initialize Database (Optional)

If you need to initialize the database with default data:

```bash
python init_fresh_db.py
```

## Running the Application

### Local Development (without Docker)

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload
```

### Docker Development

```bash
docker-compose up
```

The backend will be available at `http://localhost:8000`

## Database Management

### Accessing Your Database

You can manage your database through:
1. **Supabase Dashboard**: Visual interface at supabase.com
2. **Direct SQL**: Use the SQL Editor in Supabase Dashboard
3. **PostgreSQL Client**: Connect using any PostgreSQL client with your connection string

### Connection Pooling

The application is configured with connection pooling optimized for cloud databases:
- Pool size: 10 connections
- Max overflow: 20 connections
- Pool recycle: 3600 seconds
- Pool pre-ping: Enabled (for connection health checks)

## Troubleshooting

### Connection Issues

If you get connection errors:

1. **Check your password**: Make sure you replaced `[YOUR_PASSWORD]` with your actual Supabase database password
2. **Verify connection string**: Ensure the DATABASE_URL format is correct
3. **Check Supabase status**: Visit the Supabase dashboard to ensure your project is active
4. **Network issues**: Ensure your network allows outbound connections to Supabase

### SSL/TLS Issues

Supabase requires SSL connections. The connection string should work by default, but if you encounter SSL issues, you can add `?sslmode=require` to the end of your connection string:

```
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.xxx.supabase.co:5432/postgres?sslmode=require
```

### Migration Errors

If migrations fail:

1. **Check connection**: Ensure DATABASE_URL is set correctly
2. **Check permissions**: Ensure your Supabase user has sufficient permissions
3. **Manual check**: Use Supabase SQL Editor to check if tables already exist
4. **Reset migrations**: If needed, you can reset the alembic_version table

## Security Best Practices

1. **Never commit .env file**: The `.env` file is in `.gitignore` - keep it that way
2. **Use environment variables**: In production, use environment variables, not .env files
3. **Rotate credentials**: Regularly rotate your database password
4. **Use connection pooling**: Already configured in `database.py`
5. **Enable Row Level Security**: Consider enabling RLS in Supabase for additional security

## Next Steps

1. ✅ Set up your Supabase connection
2. ✅ Run migrations
3. ✅ Test the application
4. 📝 Configure email and Twilio settings
5. 🚀 Deploy to production

## Support

For issues with:
- **Supabase**: Visit [Supabase Documentation](https://supabase.com/docs)
- **This Application**: Check the main README.md or create an issue

---

**Note**: The PostgreSQL Docker container has been removed. All data is now stored in Supabase.

