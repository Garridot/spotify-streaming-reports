# Project Documentation: ```repositories``` Module

## Overview
The repositories module implements the Repository Pattern, acting as an abstraction layer between the domain/business logic and data persistence. It handles all database operations and encapsulates query logic.

## Base Repository Pattern
All repositories share these characteristics:

* Receive a database session in constructor
* Implement CRUD operations for specific entities
* Handle transactions and session management
* Convert between domain models and persistence models

## Key Components
| File | Responsibility |
|------|----------------|
| `user_repository.py` | Manages `User` entity persistence |
| `spotify_repository.py` | Handles Spotify credential storage |



## Design Principles
1. Single Responsibility:
* Each repository handles one entity type
* Contains only persistence logic
2. Persistence Ignorance:
* Domain models don't know about persistence
* Repositories handle model-to-database conversion
3. Explicit Transactions:
* Commits happen at repository level
* Callers don't manage transactions directly

## Related Docs
- [Database Schema](../docs/schema.md)
- [Service Layer](../services/README.md)