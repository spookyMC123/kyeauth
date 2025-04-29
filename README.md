# KeyAuth - License Key Management System

A complete authentication and license key management system with a FastAPI backend and C# WinForms client.

## Features

- User authentication with JWT tokens
- License key management (Trial, Monthly, Lifetime)
- Hardware ID (HWID) binding
- Admin panel for user and license management
- C# client application with clean UI

## Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory with:
```env
JWT_SECRET_KEY=your_secret_key_here
```

3. Run the FastAPI server:
```bash
python main.py
```

The server will start at `http://localhost:8000`

## C# Client Setup

1. Open the solution in Visual Studio
2. Install required NuGet packages:
   - System.Management
   - System.Text.Json

3. Build and run the client application

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register new user
- POST `/api/auth/login` - Login user
- GET `/api/auth/me` - Get current user info

### License Management
- POST `/api/license/activate` - Activate license key
- POST `/api/license/validate` - Validate license key
- GET `/api/license/status` - Get license status

### Admin Routes
- GET `/api/admin/users` - List all users
- POST `/api/admin/generate-key` - Generate new license key
- GET `/api/admin/licenses` - List all licenses
- POST `/api/admin/revoke-license/{license_id}` - Revoke license
- POST `/api/admin/extend-license/{license_id}` - Extend license duration

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Hardware ID binding
- Admin-only protected routes

## Database

The system uses SQLite database stored in `database/database.db`. Tables are automatically created on first run.

## License Types

- Trial: Short-term evaluation license
- Monthly: 30-day subscription license
- Lifetime: Perpetual license

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.