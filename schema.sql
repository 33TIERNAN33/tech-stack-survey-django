PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS requests;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS survivors;
DROP TABLE IF EXISTS donors;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('public', 'donor', 'survivor', 'volunteer', 'staff')),
    is_approved INTEGER NOT NULL DEFAULT 0 CHECK (is_approved IN (0, 1))
);

CREATE TABLE donors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    anonymous INTEGER NOT NULL DEFAULT 0 CHECK (anonymous IN (0, 1))
);

CREATE TABLE survivors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_info TEXT
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    storage_location TEXT,
    image_path TEXT,
    donor_id INTEGER,
    assigned_to INTEGER,
    status TEXT NOT NULL DEFAULT 'available'
        CHECK (status IN ('available', 'distributed')),
    created_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES donors(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to) REFERENCES survivors(id) ON DELETE SET NULL
);

CREATE TABLE requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    request_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'approved', 'denied')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_items_name ON items(name);
CREATE INDEX idx_items_status ON items(status);
CREATE INDEX idx_items_created_date ON items(created_date);
CREATE INDEX idx_requests_user_id ON requests(user_id);
CREATE INDEX idx_requests_item_id ON requests(item_id);
CREATE INDEX idx_requests_status ON requests(status);
