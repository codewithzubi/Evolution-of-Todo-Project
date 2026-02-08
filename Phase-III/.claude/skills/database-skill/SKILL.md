---
name: "database-design"
description: "Design database schemas, create tables with proper constraints, and generate migrations for relational databases. Use when the user needs database schema design, table creation, or migration files."
version: "1.0.0"
---

# Database Schema Design Skill

## When to Use This Skill
- When the user asks to "create a database schema" or "design tables"
- When the user mentions migrations, database structure, or data modeling
- When the user needs help with SQL table definitions or schema changes
- When planning data relationships, indexes, or constraints

## Procedure

1. **Understand the domain**: Clarify the business requirements and data entities
2. **Identify entities and relationships**: Determine tables and how they relate (1:1, 1:N, N:M)
3. **Design schema**: Define columns, data types, constraints, and indexes
4. **Apply normalization**: Ensure proper normal forms (typically 3NF) unless denormalization is justified
5. **Generate migrations**: Create sequential migration files with up/down methods
6. **Add indexes strategically**: Index foreign keys and frequently queried columns

## Output Format

**Schema Overview**: Brief description of the database purpose and main entities

**Entity Relationship Summary**: List of tables and their relationships

**Table Definitions**: For each table:
- Table name (plural, snake_case)
- Columns with data types and constraints
- Primary key
- Foreign keys
- Indexes
- Unique constraints

**Migration Files**: Sequential numbered migrations with:
- Timestamp or version number
- Up migration (create table)
- Down migration (drop table)

**Example SQL**: Complete CREATE TABLE statements ready to execute

## Quality Criteria

### Naming Conventions
- Tables: plural, snake_case (`users`, `order_items`)
- Columns: singular, snake_case (`email`, `created_at`)
- Foreign keys: `{singular_table}_id` (`user_id`, `product_id`)
- Indexes: `idx_{table}_{column(s)}` (`idx_users_email`)
- Constraints: `{table}_{column}_{type}` (`users_email_unique`)

### Schema Best Practices
- **Always include**: `id` (primary key), `created_at`, `updated_at`
- **Use appropriate types**: 
  - VARCHAR(255) for short text, TEXT for long content
  - INTEGER for counts, DECIMAL for money
  - TIMESTAMP for dates/times, BOOLEAN for flags
  - UUID for distributed systems or public IDs
- **Add constraints**:
  - NOT NULL for required fields
  - UNIQUE for fields that must be distinct
  - CHECK constraints for data validation
  - CASCADE or RESTRICT for foreign keys appropriately
- **Index strategically**:
  - Primary keys (automatic)
  - Foreign keys (manual)
  - Frequently searched columns
  - Columns used in WHERE, ORDER BY, JOIN

### Normalization Guidelines
- **1NF**: Atomic values, no repeating groups
- **2NF**: No partial dependencies (full primary key required)
- **3NF**: No transitive dependencies (non-key attributes depend only on key)
- **Denormalize intentionally**: Only for performance with clear justification

### Migration Best Practices
- One logical change per migration
- Always provide rollback (down migration)
- Make migrations idempotent when possible
- Never modify existing migrations after deployment
- Use consistent timestamp format: `YYYYMMDDHHMMSS`

## Common Patterns

### One-to-Many (User has many Posts)
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_posts_user_id (user_id)
);
```

### Many-to-Many (Students and Courses)
```sql
CREATE TABLE students (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE courses (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL
);

CREATE TABLE enrollments (
  id SERIAL PRIMARY KEY,
  student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (student_id, course_id),
  INDEX idx_enrollments_student_id (student_id),
  INDEX idx_enrollments_course_id (course_id)
);
```

### Polymorphic Associations (Comments on multiple types)
```sql
CREATE TABLE comments (
  id SERIAL PRIMARY KEY,
  commentable_type VARCHAR(50) NOT NULL, -- 'Post', 'Photo', etc.
  commentable_id INTEGER NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_comments_polymorphic (commentable_type, commentable_id)
);
```

## Example

**Input**: "I need a database schema for an e-commerce store with products, orders, and customers"

**Output**:

### Schema Overview
E-commerce database supporting customer accounts, product catalog, and order management with line items.

### Entity Relationship Summary
- `customers` (1) → (N) `orders`
- `orders` (1) → (N) `order_items`
- `products` (1) → (N) `order_items`
- `categories` (1) → (N) `products`

### Table Definitions

#### customers
- `id` - SERIAL PRIMARY KEY
- `email` - VARCHAR(255) NOT NULL UNIQUE
- `full_name` - VARCHAR(255) NOT NULL
- `password_hash` - VARCHAR(255) NOT NULL
- `created_at` - TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at` - TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- **Indexes**: `idx_customers_email` on `email`

#### categories
- `id` - SERIAL PRIMARY KEY
- `name` - VARCHAR(100) NOT NULL UNIQUE
- `slug` - VARCHAR(100) NOT NULL UNIQUE
- `created_at` - TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- **Indexes**: `idx_categories_slug` on `slug`

#### products
- `id` - SERIAL PRIMARY KEY
- `category_id` - INTEGER REFERENCES categories(id) ON DELETE SET NULL
- `name` - VARCHAR(255) NOT NULL
- `slug` - VARCHAR(255) NOT NULL UNIQUE
- `description` - TEXT
- `price` - DECIMAL(10,2) NOT NULL CHECK (price >= 0)
- `stock_quantity` - INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0)
- `is_active` - BOOLEAN NOT NULL DEFAULT true
- `created_at` - TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at` - TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- **Indexes**: 
  - `idx_products_category_id` on `category_id`
  - `idx_products_slug` on `slug`
  - `idx_products_active` on `is_active, created_at` (for browsing)

#### orders
- `id` - SERIAL PRIMARY KEY
- `customer_id` - INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE
- `status` - VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled'))
- `total_amount` - DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0)
- `shipping_address` - TEXT NOT NULL
- `created_at` - TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at` - TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- **Indexes**: 
  - `idx_orders_customer_id` on `customer_id`
  - `idx_orders_status` on `status, created_at`

#### order_items
- `id` - SERIAL PRIMARY KEY
- `order_id` - INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE
- `product_id` - INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT
- `quantity` - INTEGER NOT NULL CHECK (quantity > 0)
- `unit_price` - DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0)
- `subtotal` - DECIMAL(10,2) NOT NULL CHECK (subtotal >= 0)
- `created_at` - TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- **Indexes**: 
  - `idx_order_items_order_id` on `order_id`
  - `idx_order_items_product_id` on `product_id`

### Migration Files

**Migration: 20260118001_create_customers.sql**
```sql
-- Up
CREATE TABLE customers (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  full_name VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_email ON customers(email);

-- Down
DROP TABLE IF EXISTS customers;
```

**Migration: 20260118002_create_categories.sql**
```sql
-- Up
CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  slug VARCHAR(100) NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_slug ON categories(slug);

-- Down
DROP TABLE IF EXISTS categories;
```

**Migration: 20260118003_create_products.sql**
```sql
-- Up
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(255) NOT NULL UNIQUE,
  description TEXT,
  price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
  stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_products_active ON products(is_active, created_at);

-- Down
DROP TABLE IF EXISTS products;
```

**Migration: 20260118004_create_orders.sql**
```sql
-- Up
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  status VARCHAR(50) NOT NULL DEFAULT 'pending' 
    CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')),
  total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
  shipping_address TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status, created_at);

-- Down
DROP TABLE IF EXISTS orders;
```

**Migration: 20260118005_create_order_items.sql**
```sql
-- Up
CREATE TABLE order_items (
  id SERIAL PRIMARY KEY,
  order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
  subtotal DECIMAL(10,2) NOT NULL CHECK (subtotal >= 0),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- Down
DROP TABLE IF EXISTS order_items;
```

## Database-Specific Notes

### PostgreSQL
- Use `SERIAL` or `BIGSERIAL` for auto-incrementing IDs
- Use `TIMESTAMP` (not DATETIME)
- Support for JSONB for flexible data
- Advanced indexes: GiST, GIN for full-text search

### MySQL
- Use `AUTO_INCREMENT` for IDs
- Use `DATETIME` or `TIMESTAMP`
- InnoDB engine for foreign key support
- Use `ENGINE=InnoDB` explicitly

### SQLite
- Use `INTEGER PRIMARY KEY` for auto-increment
- Limited ALTER TABLE support (recreate tables for schema changes)
- No native BOOLEAN (use INTEGER 0/1)

## Anti-Patterns to Avoid

❌ **Don't**: Use generic column names like `data`, `value`, `info`  
✅ **Do**: Use descriptive names like `email`, `price`, `description`

❌ **Don't**: Store multiple values in one column (comma-separated)  
✅ **Do**: Create a junction table for many-to-many relationships

❌ **Don't**: Use VARCHAR(MAX) or TEXT for everything  
✅ **Do**: Choose appropriate lengths (VARCHAR(255) for emails, etc.)

❌ **Don't**: Forget indexes on foreign keys  
✅ **Do**: Always index foreign key columns

❌ **Don't**: Over-index (every column)  
✅ **Do**: Index strategically based on query patterns

❌ **Don't**: Use natural keys when they can change (email as primary key)  
✅ **Do**: Use surrogate keys (auto-incrementing IDs)

## Additional Considerations

- **Soft Deletes**: Add `deleted_at TIMESTAMP NULL` for recoverable deletes
- **Auditing**: Consider `created_by`, `updated_by` columns for user tracking
- **Versioning**: Add `version` or `row_version` for optimistic locking
- **Performance**: Use EXPLAIN to analyze query performance
- **Security**: Never store passwords in plain text (use password_hash)
- **Backups**: Always have a backup strategy before running migrations