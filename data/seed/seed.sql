INSERT INTO customers (id, name, email) VALUES
    ('cus_001', 'Ava Rodriguez', 'ava@example.test'),
    ('cus_002', 'Noah Kim', 'noah@example.test');

INSERT INTO orders (
    id, customer_id, status, ordered_at, estimated_delivery_date, total_cents
) VALUES
    ('ord_1001', 'cus_001', 'delivered', '2026-07-05', '2026-07-10', 27998),
    ('ord_1002', 'cus_001', 'shipped',   '2026-07-18', '2026-07-23', 12999),
    ('ord_2001', 'cus_002', 'processing','2026-07-20', NULL,         17999);

INSERT INTO order_items (
    id, order_id, product_name, quantity, unit_price_cents
) VALUES
    ('item_001', 'ord_1001', 'Studio Pro Headphones', 1, 24999),
    ('item_002', 'ord_1001', 'Studio Pro Travel Case', 1, 2999),
    ('item_003', 'ord_1002', 'Orbit Buds', 1, 12999),
    ('item_004', 'ord_2001', 'Pulse Mini Speaker', 1, 17999);
