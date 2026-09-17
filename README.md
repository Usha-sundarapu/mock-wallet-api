# Mock Wallet API

A backend payment system built using Python, FastAPI, MySQL, and SQLAlchemy.

This project simulates a digital wallet payment system where users can make payments to merchants, transactions are recorded, insufficient balance is handled, and API access is protected using JWT authentication.

## Features

- User and merchant management
- Wallet balance management
- Payment initialization API
- Successful and failed transactions
- Insufficient balance handling
- SQL transaction records
- Row-level locking for concurrent payments
- JWT authentication
- User authorization
- Payment webhook endpoint
- MySQL database integration
- REST API documentation using Swagger UI

## Tech Stack

- Python
- FastAPI
- MySQL
- SQLAlchemy
- PyMySQL
- JWT Authentication
- REST APIs
- Swagger UI
- Git & GitHub

## API Endpoints

### GET `/`

Checks whether the API is running.

### GET `/users`

Returns all users.

### POST `/login`

Generates a JWT access token for a user.

### POST `/initialize-payment`

Processes a payment from a user to a merchant.

The API:

1. Verifies the authenticated user.
2. Checks whether the user exists.
3. Checks whether the merchant exists.
4. Validates the payment amount.
5. Checks wallet balance.
6. Deducts the amount for successful payments.
7. Records the transaction.
8. Returns SUCCESS or FAILED status.

### POST `/webhooks/payment`

Simulates receiving a payment status webhook from an external payment system.

## System Architecture

![Mock Wallet API Architecture](architecture.png)

## Database

The project uses three main tables:

- `users`
- `merchants`
- `transactions`

### Users

Stores:

- User ID
- Name
- Email
- Wallet balance
- Account creation time

### Merchants

Stores:

- Merchant ID
- Name
- Email
- Creation time

### Transactions

Stores:

- Transaction ID
- Sender
- Receiver
- Amount
- Transaction status
- Timestamp

## Concurrency Handling

The payment API uses database row locking with `SELECT ... FOR UPDATE` to prevent two simultaneous payment requests from incorrectly spending the same wallet balance.

For example, if a user has ₹750 and two requests of ₹500 arrive at the same time:

- One payment succeeds.
- The other payment fails because the remaining balance is insufficient.

This simulates an important concept used in financial transaction systems.

## Authentication

The API uses JWT tokens for authentication.

Users must provide a valid Bearer token to access protected payment operations.

The API also verifies that the authenticated user matches the user making the payment.

## Running the Project

### 1. Create and activate virtual environment

```bash
python -m venv venv