# User Authentication and Database Management Documentation

This document provides comprehensive information about the user authentication system and database management modules implemented in the Energy Investment Decision Support System.

## Overview

The authentication and database management system consists of two main components:

1. **Authentication Manager** (`auth_manager.py`): Handles user registration, login, password management, and token-based authentication.
2. **Database Manager** (`db_manager.py`): Provides database operations for user accounts and project storage.

Together, these modules enable user account creation, secure authentication, and persistent storage of user projects and calculations.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API Handler                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────┐         ┌─────────────────────┐  │
│  │   Authentication      │         │  Project            │  │
│  │   Endpoints           │         │  Endpoints          │  │
│  └───────────┬───────────┘         └──────────┬──────────┘  │
│              │                                │             │
└──────────────┼────────────────────────────────┼─────────────┘
               │                                │
┌──────────────▼───────────┐      ┌─────────────▼────────────┐
│                          │      │                          │
│   AuthManager            │◄────►│   DatabaseManager        │
│                          │      │                          │
├──────────────────────────┤      ├──────────────────────────┤
│ ● User Registration      │      │ ● User Storage           │
│ ● Authentication         │      │ ● Project Management     │
│ ● Password Management    │      │ ● Data Persistence       │
│ ● Token Handling         │      │ ● Query Handling         │
└──────────────────────────┘      └──────────────────────────┘
               │                                │
               │                                │
┌──────────────▼───────────┐      ┌─────────────▼────────────┐
│    JWT Tokens            │      │      SQLite Database     │
└──────────────────────────┘      └──────────────────────────┘
```

## Authentication Manager

The Authentication Manager (`auth_manager.py`) handles all aspects of user authentication, including registration, login, token generation, and verification.

### Key Features

1. **Secure User Registration**: Creates new user accounts with hashed passwords
2. **User Authentication**: Verifies credentials and issues JWT tokens
3. **Password Management**: Secure password hashing and verification
4. **Token-based Authentication**: JWT token generation and validation
5. **User Profile Management**: Retrieves and updates user information

### Technical Implementation

#### Password Security

Passwords are securely stored using PBKDF2-HMAC-SHA256 with a random salt:

```python
def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hash a password with a salt for secure storage.
    
    Args:
        password: Plain text password
        salt: Salt string (generated if None)
        
    Returns:
        Tuple of (password_hash, salt)
    """
    if salt is None:
        salt = uuid.uuid4().hex
    
    # Create hash using PBKDF2 with SHA-256
    password_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000  # Number of iterations
    ).hex()
    
    return password_hash, salt
```

This approach:
- Uses PBKDF2, a key derivation function designed for password hashing
- Applies 100,000 iterations to increase computational cost for brute-force attacks
- Uses a unique salt for each user to prevent rainbow table attacks
- Outputs a hexadecimal hash string that can be safely stored in a database

#### JWT Token Generation

JWT (JSON Web Token) tokens are generated for authenticated users:

```python
def _generate_token(self, user_id: str, username: str) -> str:
    """Generate a JWT token for a user.
    
    Args:
        user_id: User ID
        username: Username
        
    Returns:
        JWT token string
    """
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=self.token_expiry),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id,
        'username': username
    }
    
    return jwt.encode(
        payload,
        self.secret_key,
        algorithm='HS256'
    )
```

The token includes:
- Expiration time (exp): When the token expires
- Issued at time (iat): When the token was issued
- Subject (sub): The user ID
- Username: The user's username

#### Token Verification

Tokens are verified before allowing access to protected endpoints:

```python
def verify_token(self, token: str) -> Dict[str, Any]:
    """Verify a JWT token and extract the payload.
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary with token payload
        
    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
```

### API Integration (token_required Decorator)

Protected endpoints use the `token_required` decorator:

```python
def token_required(f):
    """Decorator for Flask routes that require token authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        try:
            # Get the AuthManager instance
            auth_manager = kwargs.get('auth_manager') or AuthManager()
            
            # Verify token
            payload = auth_manager.verify_token(token)
            
            # Add user data to kwargs
            kwargs['user_id'] = payload['sub']
            kwargs['username'] = payload['username']
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated
```

This decorator:
1. Extracts the JWT token from the Authorization header
2. Verifies the token is valid and not expired
3. Adds the user ID and username to the function parameters
4. Returns an error if authentication fails

## Database Manager

The Database Manager (`db_manager.py`) handles all database operations, including user storage, project management, and data persistence.

### Key Features

1. **User Storage**: Persists user account information
2. **Project Management**: CRUD operations for user projects
3. **Data Persistence**: Stores calculation parameters and results
4. **Query Handling**: Efficiently retrieves and filters data
5. **Project Sharing**: Supports collaboration through project sharing

### Technical Implementation

#### Database Schema

The database uses SQLite with the following schema:

1. **Users Table**:
```sql
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
```

2. **Projects Table**:
```sql
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    location_lat REAL,
    location_lon REAL,
    parameters TEXT,
    results TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

3. **Shared Projects Table**:
```sql
CREATE TABLE IF NOT EXISTS shared_projects (
    project_id TEXT,
    shared_with_id TEXT,
    permissions TEXT,
    shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, shared_with_id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (shared_with_id) REFERENCES users(id)
)
```

#### Project Storage and Retrieval

Projects are stored with their parameters and calculation results:

```python
def save_project(self, 
                user_id: str, 
                name: str, 
                description: Optional[str] = None,
                location_lat: Optional[float] = None,
                location_lon: Optional[float] = None,
                parameters: Optional[Dict[str, Any]] = None,
                results: Optional[Dict[str, Any]] = None,
                project_id: Optional[str] = None) -> str:
    """Save a new project or update an existing one.
    
    Args:
        user_id: User ID
        name: Project name
        description: Project description (optional)
        location_lat: Location latitude (optional)
        location_lon: Location longitude (optional)
        parameters: Project parameters as dictionary (optional)
        results: Calculation results as dictionary (optional)
        project_id: Project ID for updates (optional, generates new ID if None)
        
    Returns:
        Project ID
    """
    # Convert parameters and results to JSON strings
    parameters_json = json.dumps(parameters) if parameters else None
    results_json = json.dumps(results) if results else None
    
    if project_id:
        # Update existing project
        query = """
        UPDATE projects
        SET name = ?, description = ?, location_lat = ?, location_lon = ?, 
            parameters = ?, results = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
        """
        self.execute_query(
            query, 
            (name, description, location_lat, location_lon, 
             parameters_json, results_json, project_id, user_id)
        )
        return project_id
    else:
        # Create new project
        project_id = str(uuid.uuid4())
        query = """
        INSERT INTO projects (
            id, user_id, name, description, location_lat, 
            location_lon, parameters, results
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_query(
            query, 
            (project_id, user_id, name, description, location_lat, 
             location_lon, parameters_json, results_json)
        )
        return project_id
```

When retrieving a project, JSON strings are parsed back into Python objects:

```python
def get_project(self, 
               project_id: str, 
               user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get a project by ID.
    
    Args:
        project_id: Project ID
        user_id: User ID (if provided, ensures the project belongs to this user)
        
    Returns:
        Project data as dictionary, or None if not found
    """
    if user_id:
        # Get project for specific user
        query = """
        SELECT * FROM projects 
        WHERE id = ? AND user_id = ?
        """
        project = self.fetch_one(query, (project_id, user_id))
    else:
        # Get project by ID only (used for shared projects)
        query = """
        SELECT * FROM projects 
        WHERE id = ?
        """
        project = self.fetch_one(query, (project_id,))
    
    if not project:
        return None
    
    # Convert project to dictionary
    result = dict(project)
    
    # Parse JSON strings
    if result.get('parameters'):
        result['parameters'] = json.loads(result['parameters'])
    
    if result.get('results'):
        result['results'] = json.loads(result['results'])
    
    return result
```

#### Project Sharing

The system supports project sharing with different permission levels:

```python
def share_project(self, 
                 project_id: str, 
                 owner_id: str, 
                 shared_with_id: str,
                 permissions: Dict[str, bool]) -> bool:
    """Share a project with another user.
    
    Args:
        project_id: Project ID
        owner_id: Owner's user ID
        shared_with_id: ID of user to share with
        permissions: Dictionary of permissions (read, edit, etc.)
        
    Returns:
        True if project was shared, False if not found or not owned by owner_id
    """
    # First check if project exists and belongs to owner
    query = "SELECT id FROM projects WHERE id = ? AND user_id = ?"
    project = self.fetch_one(query, (project_id, owner_id))
    
    if not project:
        return False
    
    # Convert permissions to JSON
    permissions_json = json.dumps(permissions)
    
    # Check if already shared
    check_query = """
    SELECT project_id FROM shared_projects 
    WHERE project_id = ? AND shared_with_id = ?
    """
    existing = self.fetch_one(check_query, (project_id, shared_with_id))
    
    if existing:
        # Update existing share
        update_query = """
        UPDATE shared_projects
        SET permissions = ?, shared_at = CURRENT_TIMESTAMP
        WHERE project_id = ? AND shared_with_id = ?
        """
        self.execute_query(update_query, (permissions_json, project_id, shared_with_id))
    else:
        # Create new share
        insert_query = """
        INSERT INTO shared_projects (project_id, shared_with_id, permissions)
        VALUES (?, ?, ?)
        """
        self.execute_query(insert_query, (project_id, shared_with_id, permissions_json))
    
    return True
```

## API Endpoints

The authentication and database systems are integrated into the API through several endpoints:

### Authentication Endpoints

#### User Registration

```
POST /api/auth/register
```

Registers a new user in the system.

**Request:**
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "username": "user123",
  "email": "user@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### User Login

```
POST /api/auth/login
```

Authenticates a user and returns a token.

**Request:**
```json
{
  "username_or_email": "user123",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "username": "user123",
  "email": "user@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Token Verification

```
GET /api/auth/verify
```

Verifies a user's authentication token and returns user information.

**Headers:**
- `Authorization`: `Bearer <token>`

**Response:**
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "username": "user123",
  "email": "user@example.com",
  "created_at": "2025-03-15T12:30:45.000Z",
  "last_login": "2025-04-12T14:30:00.000Z"
}
```

### Project Management Endpoints

#### Get Projects List

```
GET /api/projects
```

Retrieves all projects for the authenticated user.

**Headers:**
- `Authorization`: `Bearer <token>`

**Response:**
```json
{
  "projects": [
    {
      "id": "p1q2r3s4-t5u6-7890-v1w2-x3y4z5a67890",
      "name": "Residential Solar Project",
      "description": "10kW system for my home",
      "location_lat": 39.7392,
      "location_lon": -104.9903,
      "created_at": "2025-03-10T15:20:30.000Z",
      "updated_at": "2025-03-15T09:45:12.000Z"
    },
    // More projects...
  ]
}
```

#### Get Project Details

```
GET /api/projects/<project_id>
```

Retrieves details for a specific project.

**Headers:**
- `Authorization`: `Bearer <token>`

**Response:**
```json
{
  "id": "p1q2r3s4-t5u6-7890-v1w2-x3y4z5a67890",
  "name": "Residential Solar Project",
  "description": "10kW system for my home",
  "location_lat": 39.7392,
  "location_lon": -104.9903,
  "parameters": {
    "systemCapacity": 10.0,
    "moduleType": 1,
    // Other parameters...
  },
  "results": {
    "production": {
      // Production data
    },
    "financials": {
      // Financial data
    }
  },
  "created_at": "2025-03-10T15:20:30.000Z",
  "updated_at": "2025-03-15T09:45:12.000Z"
}
```

#### Create Project

```
POST /api/projects
```

Creates a new project.

**Headers:**
- `Authorization`: `Bearer <token>`

**Request:**
```json
{
  "name": "Residential Solar Project",
  "description": "10kW system for my home",
  "location_lat": 39.7392,
  "location_lon": -104.9903,
  "parameters": {
    "systemCapacity": 10.0,
    "moduleType": 1,
    // Other parameters...
  },
  "results": {
    // Calculation results
  }
}
```

**Response:**
The created project object.

#### Update Project

```
PUT /api/projects/<project_id>
```

Updates an existing project.

**Headers:**
- `Authorization`: `Bearer <token>`

**Request:**
Same as for creating a project.

**Response:**
The updated project object.

#### Delete Project

```
DELETE /api/projects/<project_id>
```

Deletes a project.

**Headers:**
- `Authorization`: `Bearer <token>`

**Response:**
```json
{
  "success": true
}
```

## Frontend Integration

The authentication and database systems are integrated with the frontend through several React components:

### Authentication Components

#### AuthProvider

The `AuthProvider` component manages authentication state and provides authentication functions to other components:

```jsx
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for existing token on component mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        if (!token) {
          setLoading(false);
          return;
        }

        const response = await fetch('/api/auth/verify', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          localStorage.removeItem('auth_token');
        }
      } catch (err) {
        console.error('Authentication error:', err);
        setError('Failed to verify authentication');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Login function
  const login = async (usernameOrEmail, password) => {
    // Implementation...
  };

  // Register function
  const register = async (username, email, password) => {
    // Implementation...
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
  };

  // Function to get auth token
  const getToken = () => {
    return localStorage.getItem('auth_token');
  };

  // Function for authenticated fetch
  const authFetch = async (url, options = {}) => {
    const token = getToken();
    
    if (!token) {
      throw new Error('Authentication required');
    }

    const authOptions = {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    };

    const response = await fetch(url, authOptions);
    
    // If we get a 401 Unauthorized, the token may be invalid or expired
    if (response.status === 401) {
      logout();
      throw new Error('Session expired. Please log in again.');
    }
    
    return response;
  };

  // Create context value
  const contextValue = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    getToken,
    authFetch,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

#### LoginForm and RegisterForm

These components provide user interfaces for authentication:

```jsx
const LoginForm = ({ onSuccess }) => {
  const { login, loading, error } = useAuth();
  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [password, setPassword] = useState('');
  const [formError, setFormError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    // Basic validation
    if (!usernameOrEmail.trim() || !password) {
      setFormError('Please enter both username/email and password');
      return;
    }

    try {
      await login(usernameOrEmail, password);
      
      // Call the success callback if provided
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      setFormError(err.message || 'Login failed');
    }
  };

  // Form UI implementation...
};
```

### Project Management Components

#### ProjectList

Displays a list of the user's projects:

```jsx
const ProjectList = ({ onProjectSelect, onCreateNew }) => {
  const { authFetch, isAuthenticated } = useAuth();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch projects when component mounts
  useEffect(() => {
    if (isAuthenticated) {
      fetchProjects();
    } else {
      setProjects([]);
      setLoading(false);
    }
  }, [isAuthenticated]);

  const fetchProjects = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await authFetch('/api/projects');
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to fetch projects');
      }
      
      const data = await response.json();
      setProjects(data.projects || []);
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError('Failed to load projects. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Implementation for loading, deleting projects...
};
```

#### SaveProjectForm

Provides a form for saving or updating a project:

```jsx
const SaveProjectForm = ({ 
  projectData,
  location,
  calculationResults,
  onSuccess,
  onCancel,
  existingProject = null
}) => {
  const { authFetch, isAuthenticated } = useAuth();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Set initial form values when editing an existing project
  useEffect(() => {
    if (existingProject) {
      setName(existingProject.name || '');
      setDescription(existingProject.description || '');
    }
  }, [existingProject]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    // Validation and submission implementation...
  };

  // Form UI implementation...
};
```

## Best Practices for Security and Performance

### Security Best Practices

1. **Password Storage**:
   - Use PBKDF2 or Argon2 for password hashing
   - Use a unique salt for each user
   - Use a high number of iterations (100,000+)

2. **Token Security**:
   - Keep token expiration time reasonable (24 hours is common)
   - Store the JWT secret key securely (environment variable)
   - Validate tokens on every protected request

3. **Database Security**:
   - Use parameterized queries to prevent SQL injection
   - Validate input data before storage
   - Implement proper access control for user data

4. **Error Handling**:
   - Don't expose sensitive information in error messages
   - Log authentication failures for security monitoring
   - Implement rate limiting to prevent brute force attacks

### Performance Considerations

1. **Database Optimization**:
   - Create appropriate indexes for commonly queried fields
   - Use connection pooling for better performance
   - Implement efficient query patterns

2. **Token Handling**:
   - Keep JWT payload size minimal for better performance
   - Consider using refresh tokens for long sessions

3. **Project Storage**:
   - Consider pagination for users with many projects
   - Optimize large result data storage (possible compression)

## Deployment Considerations

1. **Environment Configuration**:
   - Use environment variables for configuration
   - Set the JWT_SECRET_KEY environment variable in production
   - Configure database paths appropriately

2. **Database Security**:
   - In production, consider using a more robust database system (PostgreSQL, MySQL)
   - Implement regular backups
   - Use connection encryption

3. **Token Lifetime**:
   - Adjust token expiry based on security requirements
   - Consider implementing refresh tokens for better UX

## Future Enhancements

1. **Enhanced Authentication**:
   - Two-factor authentication
   - Social login integration
   - Email verification

2. **Advanced Project Management**:
   - Folders or tags for project organization
   - Enhanced sharing permissions
   - Project templates

3. **Audit and Activity Logging**:
   - Track user activity for security
   - Log project changes
   - Implement undo/redo functionality