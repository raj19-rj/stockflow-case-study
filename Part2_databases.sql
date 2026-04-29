-- Part 2: Database Design
-- ========================
-- 8 tables covering all requirements
-- Includes: audit trail, bundles, suppliers, inventory tracking

-- Companies
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Warehouses (companies have multiple)
CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    location TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Suppliers
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Products
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) NOT NULL UNIQUE,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    product_type VARCHAR(50) DEFAULT 'standard',
    low_stock_threshold INT DEFAULT 10,
    supplier_id INT REFERENCES suppliers(id),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Product Bundles (bundle products contain other products)
CREATE TABLE product_bundles (
    bundle_product_id INT REFERENCES products(id),
    component_product_id INT REFERENCES products(id),
    quantity INT NOT NULL DEFAULT 1,
    PRIMARY KEY (bundle_product_id, component_product_id)
);

-- Inventory (per product per warehouse)
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id),
    warehouse_id INT NOT NULL REFERENCES warehouses(id),
    quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    UNIQUE(product_id, warehouse_id)
);

-- Inventory Logs (audit trail for all changes)
CREATE TABLE inventory_logs (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id),
    warehouse_id INT NOT NULL REFERENCES warehouses(id),
    change_quantity INT NOT NULL,
    reason VARCHAR(100), -- 'sale', 'restock', 'adjustment'
    changed_at TIMESTAMP DEFAULT NOW()
);

-- Sales Activity
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id),
    warehouse_id INT NOT NULL REFERENCES warehouses(id),
    quantity_sold INT NOT NULL,
    sold_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_inventory_product ON inventory(product_id);
CREATE INDEX idx_inventory_warehouse ON inventory(warehouse_id);
CREATE INDEX idx_sales_product_date ON sales(product_id, sold_at);
CREATE INDEX idx_products_company ON products(company_id);

/*
GAPS / QUESTIONS FOR PRODUCT TEAM:
1. What defines "recent" sales - last 7 or 30 days?
2. Is threshold per product or per product category?
3. Can a product belong to multiple companies?
4. How are bundle stock levels calculated?
5. Do we need multi-currency support?
6. Is there "reserved" stock for pending orders?
*/
