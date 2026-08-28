-- Domínio de Referência, contract_version 1.
-- timestamptz(3): a precisão de milissegundo exigida por
-- specs/reference-domain/domain.md é imposta pelo próprio banco, o que remove
-- uma classe inteira de divergência entre linguagens.

CREATE TABLE categories (
    id   bigserial PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE products (
    id          bigserial PRIMARY KEY,
    sku         text        NOT NULL,
    name        text        NOT NULL,
    price_cents integer     NOT NULL CHECK (price_cents >= 0),
    stock       integer     NOT NULL CHECK (stock >= 0),
    category_id bigint      NOT NULL REFERENCES categories (id),
    attrs       jsonb       NOT NULL,
    created_at  timestamptz(3) NOT NULL
);

CREATE UNIQUE INDEX uq_products_sku ON products (sku);
CREATE INDEX idx_products_created_id ON products (created_at DESC, id DESC);
CREATE INDEX idx_products_category_created ON products (category_id, created_at DESC, id DESC);
CREATE INDEX idx_products_name_prefix ON products (lower(name) text_pattern_ops);

CREATE TABLE customers (
    id         bigserial PRIMARY KEY,
    email      text NOT NULL,
    name       text NOT NULL,
    created_at timestamptz(3) NOT NULL
);

CREATE UNIQUE INDEX uq_customers_email ON customers (email);

CREATE TABLE orders (
    id              bigserial PRIMARY KEY,
    customer_id     bigint  NOT NULL REFERENCES customers (id),
    status          text    NOT NULL CHECK (status IN ('pending', 'paid', 'shipped', 'cancelled')),
    total_cents     integer NOT NULL CHECK (total_cents >= 0),
    idempotency_key text    NOT NULL,
    created_at      timestamptz(3) NOT NULL
);

CREATE UNIQUE INDEX uq_orders_idempotency_key ON orders (idempotency_key);
CREATE INDEX idx_orders_customer_created ON orders (customer_id, created_at DESC, id DESC);

CREATE TABLE order_items (
    order_id         bigint  NOT NULL REFERENCES orders (id),
    product_id       bigint  NOT NULL REFERENCES products (id),
    qty              integer NOT NULL CHECK (qty > 0),
    unit_price_cents integer NOT NULL CHECK (unit_price_cents >= 0),
    PRIMARY KEY (order_id, product_id)
);
