# AR Enhanced Maintenance Support System

This project is a university group coursework submission for the unit Technological Innovations in Computing  at Bournemouth University. It demonstrates a proof-of-concept augmented-reality maintenance support system for high-security engineering environments, developed as a multi-pathway collaborative effort.

A fault tracking and maintenance management platform with JWT authentication, role-based access, a supervisor dashboard, and AR visualization capabilities. The system allows maintenance engineers to report, monitor, and resolve faults via a web interface, while supervisors can oversee operations through a real-time dashboard. An augmented reality view enables on-site personnel to visualise fault details and tool status using marker-based tracking.

## Live Demo

**View the live application**: [https://ar-emss.onrender.com/](https://ar-emss.onrender.com/)

*Note: The live demo may take a few seconds to load as it's running on Render's free tier.*

## Team

- Artem Potejevs – Cyber Security Pathway
- Carlos Reeves – Computing Pathway
- Rafael Freitas – Computing Pathway
- Tawanda Gabaza – Cyber Security Pathway
- Vishal Shanmugam – Cyber Security Pathway

## Current Project Status

### Core Features Implemented

#### 1. **Authentication & Authorization**
- JWT token-based authentication with 1-hour expiry
- Bcrypt password hashing for secure storage
- Bearer token validation on protected routes
- User registration and login endpoints
- Role-based system (Engineer, Supervisor roles)

#### 2. **Fault Tracker (Fault Tracker Page)**
- **Report Fault Card**: Submit new faults with title, location, and severity (Low/Medium/High)
- **Basic Metrics Card**: Display total, open, resolved, and high-severity fault counts
- **Faults List Card**: Dynamic fault listing with real-time status updates
- **Color-Coded Action Buttons**:
  - Green "Resolve" button when fault status = "open" 
  - Yellow "Reopen" button when fault status = "closed" (resolved)
  - Red "Delete" button for removing faults
- **Navigation**: Links to Supervisor Dashboard and AR View, Logout functionality
- Consistent navigation styling across all pages

#### 3. **Supervisor Dashboard**
- **Fault Overview Metrics**: Total faults, Open, Resolved, High Severity counts displayed as stat cards
- **Chart Visualizations**:
  - Fault Status Chart: Doughnut chart showing Open vs Resolved distribution
  - Severity Distribution Chart: Bar chart showing Low/Medium/High severity breakdown
- **Tool Inventory Metrics**: Total Tools, Checked In, Checked Out counts
- **Tool Availability Chart**: Doughnut chart showing Checked In vs Checked Out distribution
- **Recent Activity Feed**: Scrollable card displaying recent fault updates with timestamps (Just now, minutes ago, hours ago format)
- **Responsive Design**: Charts and metrics adapt to screen size with media queries for mobile (640px, 400px breakpoints)
- **High-DPI Support**: Canvas charts scale properly on high-resolution displays using devicePixelRatio
- **Error Handling**: Error banner displays API failures with dismissal support
- **Loading State**: Spinner animation shown while fetching data
- **Last Updated Timestamp**: Shows when dashboard was last refreshed

#### 4. **AR View**
- Dedicated page for augmented reality fault visualization
- Accessible from navigation menu across all pages

#### 5. **Backend API**

##### Authentication Routes
- `POST /register` - User registration with username/password
- `POST /login` - Login returning JWT access token

##### Fault Management Routes
- `GET /api/faults` - List all faults (with optional filtering)
- `POST /api/faults` - Create new fault (requires: title, location, severity)
- `GET /api/faults/{id}` - Retrieve specific fault
- `PATCH /api/faults/{id}` - Update fault (title, location, severity, status)
- `DELETE /api/faults/{id}` - Delete fault
- `GET /api/recent-activity` - Get recent fault activity feed for dashboard

##### Tool Management Routes
- `GET /api/tools` - List all tools
- `POST /api/tools` - Create new tool (requires: name, status)
- `GET /api/tools/{id}` - Retrieve specific tool
- `PATCH /api/tools/{id}` - Update tool (name, status)

##### Page Routes
- `GET /` - Fault Tracker dashboard page
- `GET /dashboard` - Supervisor Dashboard
- `GET /ar` - AR View page
- `GET /docs` - Swagger API documentation (FastAPI built-in)

#### 6. **Data Models**

##### Fault Model
- `id`: Primary key
- `title`: Fault description (required)
- `location`: Physical location of fault (required)
- `severity`: 1-3 scale (Low/Medium/High)
- `status`: "open" or "closed"
- `user_id`: Foreign key to User (fault reporter)
- `created_at`: Timestamp
- `updated_at`: Timestamp
- `owner`: Relationship to User model

##### Tool Model
- `id`: Primary key
- `name`: Tool name
- `status`: "checked_in" or "checked_out"
- `created_at`: Timestamp
- `updated_at`: Timestamp

##### User Model
- `id`: Primary key
- `username`: Unique identifier
- `password`: Bcrypt hashed
- `role`: Default "Engineer", can be "Supervisor"
- `faults`: Relationship to Fault model

#### 7. **Frontend Architecture**

##### Static Files Structure
- **index.html**: Fault Tracker main page with login overlay, report form, metrics, and fault list
- **dashboard.html**: Supervisor dashboard with charts, metrics, and recent activity feed
- **ar.html**: AR view page (stub for augmentation)
- **api.js**: Centralized API communication layer with Bearer token authentication
- **ui.js**: UI rendering functions (renderFaults with escapeHtml XSS prevention)
- **main.js**: Event handling, authentication gate, dashboard state management

##### CSS Features
- Flexbox and CSS Grid responsive layouts
- Color-coded visual hierarchy for status indication
- Media queries for mobile optimization (640px, 400px breakpoints)
- Smooth animations (spinner, button hover states)
- High-DPI canvas chart scaling
- Consistent card-based UI design

#### 8. **Error Handling**
- Standardized JSON error responses with `{ok: false, error: {message}}`
- HTTP exception handling with proper status codes
- Pydantic validation error responses (422)
- Server error handling (500 with user-friendly messages)
- XSS prevention via HTML entity escaping in UI rendering

#### 9. **Testing**
- Comprehensive pytest test suite in `test_main.py`
- Test coverage for:
  - Authentication flow (register/login)
  - Fault CRUD operations
  - Tool CRUD operations
  - Fault filtering and status updates
  - Error cases (404, validation errors, auth failures)

### Project Structure

```
ar-emss/
├── main.py              # FastAPI application with all routes and middleware
├── database.py          # SQLite connection setup with thread safety
├── models.py            # SQLAlchemy ORM models (Fault, Tool, User)
├── schemas.py           # Pydantic validation schemas for API requests/responses
├── test_main.py         # Comprehensive pytest test suite
├── requirements.txt     # Python dependencies
├── readme.md            # Project documentation
├── .gitignore           # Git ignore rules
└── static/
    ├── index.html       # Fault Tracker page with login overlay
    ├── dashboard.html   # Supervisor Dashboard with charts and metrics
    ├── ar.html          # AR View page
    ├── api.js           # Fetch API communication layer
    ├── ui.js            # UI rendering with fault cards
    ├── main.js          # Event handling and state management
    └── targets.mind     # AR targets configuration file
```

### Dependencies

**Core**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `pydantic` - Data validation
- `python-jose` - JWT token handling
- `passlib[bcrypt]` - Password hashing
- `python-multipart` - Form data parsing
- `pytest` - Testing framework
- `httpx` - HTTP client for tests

## How to Run

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Server
```bash
uvicorn main:app --reload
```

The application will start at `http://localhost:8000`

### 4. Access Pages
- **Fault Tracker**: http://localhost:8000
- **Supervisor Dashboard**: http://localhost:8000/dashboard
- **AR View**: http://localhost:8000/ar
- **API Documentation**: http://localhost:8000/docs

### 5. Run Tests
```bash
pytest test_main.py -v
```

## Login Credentials

The system uses JWT authentication. Create an account via the login form or register endpoint, then login with username/password.

### Default Admin User (Automatically created on startup)
- Username: admin
- Password: admin123
- Role: admin

