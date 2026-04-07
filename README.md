# User Management API

## Description
User Management API is a proof-of-concept API for account creation and authentication.
It is built with FastAPI and PostgreSQL with SQLAlchemy.


## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create ```.env``` file with the following parameters:

```
DATABASE_URL=postgresql://<...>
SECRET_KEY=<...>
PEPPER=<...>
```
- ```DATABASE_URL``` is the url to your postgresql server. If you use linux and created a psql user with the same name as your linux user and a database called user_management the URL will be ```postgresql://<user>@/user_management```

- ```SECRET_KEY``` is the key used to create JSON Web Tokens.

- ```PEPPER``` is an optional string parameter for adding peppering when hashing passwords.

3. Run API server:
```bash
fastapi dev
```

4. Run tests:
```bash
pytest
```

## Authentication flow
1. Create a user with `POST /users`.
2. Authenticate with `POST /login` to get a bearer token.
3. Call protected endpoints (for example `GET /users/self`) with:

```http
Authorization: Bearer <access_token>
```

## Endpoints

### `GET /`
Returns a welcome message.

**Response `200`**
```json
{
	"message": "Welcome to Hugo Björs's user management API..."
}
```

---

### `POST /users`
Creates a user.

**Request body (JSON)**
```json
{
	"email": "user@example.com",
	"password": "your-password"
}
```

**Responses**
- `201 Created`
```json
{
	"message": "User created",
	"username": "<uuid>"
}
```
- `409 Conflict` when constraints are violated (for example duplicate user data).
- `500 Internal Server Error` for unexpected database errors.

---

### `POST /login`
Authenticates a user and returns a JWT access token.

This endpoint uses `OAuth2PasswordRequestForm`, so data must be sent as
`application/x-www-form-urlencoded` (not JSON).

**Request body (form fields)**
- `username`: UUID string returned by `POST /users`
- `password`: user password

**Responses**
- `200 OK`
```json
{
	"message": "Login successful",
	"token": {
		"access_token": "<jwt>",
		"token_type": "bearer"
	}
}
```
- `401 Unauthorized` for invalid credentials.

---

### `GET /users/self`
Returns the currently authenticated user.

**Headers**
```http
Authorization: Bearer <access_token>
```

**Responses**
- `200 OK` with user data.
- `401 Unauthorized` if token is missing, invalid, or user no longer exists.

---

### `PUT /change_password`
Changes the password for the currently authenticated user.

**Headers**
```http
Authorization: Bearer <access_token>
```

**Request body (JSON)**
```json
{
	"password": "new-password"
}
```

**Responses**
- `200 OK`
```json
{
	"message": "Password changed",
	"username": "<uuid>"
}
```
- `401 Unauthorized` if token is missing, invalid, or user no longer exists.
- `500 Internal Server Error` for unexpected database errors.

---
