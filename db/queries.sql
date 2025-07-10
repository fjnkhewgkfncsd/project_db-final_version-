-- Complex SQL Queries for E-Commerce Database
-- 15+ Complex Queries with Joins, Subqueries, Aggregations, Functions, and Stored Procedures

-- Query 1: Top 10 customers by total spending with order statistics
-- Performance: Uses joins and aggregations
SELECT 
    u.user_id,
    u.first_name || ' ' || u.last_name AS customer_name,
    u.email,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.final_amount) AS total_spent,
    AVG(o.final_amount) AS avg_order_value,
    MAX(o.created_at) AS last_order_date,
    RANK() OVER (ORDER BY SUM(o.final_amount) DESC) AS spending_rank
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.order_status IN ('delivered', 'shipped')
GROUP BY u.user_id, u.first_name, u.last_name, u.email
HAVING SUM(o.final_amount) > 1000
ORDER BY total_spent DESC
LIMIT 10;

-- Query 2: Product performance analysis with category hierarchy
-- Performance: Complex joins with recursive CTE for category hierarchy
WITH RECURSIVE category_hierarchy AS (
    -- Base case: root categories
    SELECT category_id, name, parent_category_id, name as root_category, 1 as level
    FROM categories 
    WHERE parent_category_id IS NULL
    
    UNION ALL
    
    -- Recursive case: subcategories
    SELECT c.category_id, c.name, c.parent_category_id, ch.root_category, ch.level + 1
    FROM categories c
    JOIN category_hierarchy ch ON c.parent_category_id = ch.category_id
),
product_sales AS (
    SELECT 
        p.product_id,
        p.name,
        p.brand,
        p.base_price,
        COUNT(oi.order_item_id) AS units_sold,
        SUM(oi.total_price) AS total_revenue,
        AVG(oi.unit_price) AS avg_selling_price
    FROM products p
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered' OR o.order_status IS NULL
    GROUP BY p.product_id, p.name, p.brand, p.base_price
)
SELECT 
    ch.root_category,
    ps.name AS product_name,
    ps.brand,
    ps.base_price,
    ps.units_sold,
    ps.total_revenue,
    ps.avg_selling_price,
    ROUND((ps.avg_selling_price - ps.base_price) / ps.base_price * 100, 2) AS price_variance_pct,
    ROW_NUMBER() OVER (PARTITION BY ch.root_category ORDER BY ps.total_revenue DESC) AS category_rank
FROM product_sales ps
JOIN products p ON ps.product_id = p.product_id
JOIN category_hierarchy ch ON p.category_id = ch.category_id
WHERE ps.units_sold > 0
ORDER BY ch.root_category, ps.total_revenue DESC;

-- Query 3: Monthly sales trend with year-over-year comparison
-- Performance: Window functions and date aggregations
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', created_at) AS month,
        EXTRACT(YEAR FROM created_at) AS year,
        EXTRACT(MONTH FROM created_at) AS month_num,
        COUNT(*) AS order_count,
        SUM(final_amount) AS total_revenue,
        AVG(final_amount) AS avg_order_value
    FROM orders 
    WHERE order_status = 'delivered'
    GROUP BY DATE_TRUNC('month', created_at), EXTRACT(YEAR FROM created_at), EXTRACT(MONTH FROM created_at)
)
SELECT 
    month,
    year,
    month_num,
    order_count,
    total_revenue,
    avg_order_value,
    LAG(total_revenue, 12) OVER (ORDER BY month) AS prev_year_revenue,
    ROUND(
        CASE 
            WHEN LAG(total_revenue, 12) OVER (ORDER BY month) IS NOT NULL 
            THEN ((total_revenue - LAG(total_revenue, 12) OVER (ORDER BY month)) / 
                  LAG(total_revenue, 12) OVER (ORDER BY month) * 100)
            ELSE NULL 
        END, 2
    ) AS yoy_growth_pct,
    SUM(total_revenue) OVER (PARTITION BY year ORDER BY month_num ROWS UNBOUNDED PRECEDING) AS ytd_revenue
FROM monthly_sales
ORDER BY month;

-- Query 4: Customer segmentation based on RFM analysis (Recency, Frequency, Monetary)
-- Performance: Complex analytical functions
WITH customer_rfm AS (
    SELECT 
        u.user_id,
        u.first_name || ' ' || u.last_name AS customer_name,
        u.email,
        CURRENT_DATE - MAX(o.created_at)::date AS recency_days,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(o.final_amount) AS monetary_value,
        AVG(o.final_amount) AS avg_order_value
    FROM users u
    JOIN orders o ON u.user_id = o.user_id
    WHERE o.order_status IN ('delivered', 'shipped')
    GROUP BY u.user_id, u.first_name, u.last_name, u.email
),
rfm_scores AS (
    SELECT 
        *,
        NTILE(5) OVER (ORDER BY recency_days) AS recency_score,
        NTILE(5) OVER (ORDER BY frequency DESC) AS frequency_score,
        NTILE(5) OVER (ORDER BY monetary_value DESC) AS monetary_score
    FROM customer_rfm
),
customer_segments AS (
    SELECT 
        *,
        (frequency_score + monetary_score) / 2.0 AS fm_score,
        CASE 
            WHEN recency_score >= 4 AND (frequency_score + monetary_score) / 2.0 >= 4 THEN 'Champions'
            WHEN recency_score >= 3 AND (frequency_score + monetary_score) / 2.0 >= 3 THEN 'Loyal Customers'
            WHEN recency_score >= 3 AND frequency_score >= 2 THEN 'Potential Loyalists'
            WHEN recency_score >= 4 AND frequency_score <= 2 THEN 'New Customers'
            WHEN recency_score >= 2 AND (frequency_score + monetary_score) / 2.0 >= 3 THEN 'At Risk'
            WHEN recency_score <= 2 AND (frequency_score + monetary_score) / 2.0 >= 3 THEN 'Cannot Lose Them'
            WHEN recency_score <= 2 AND frequency_score <= 2 THEN 'Lost'
            ELSE 'Others'
        END AS customer_segment
    FROM rfm_scores
)
SELECT 
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(recency_days), 1) AS avg_recency,
    ROUND(AVG(frequency), 1) AS avg_frequency,
    ROUND(AVG(monetary_value), 2) AS avg_monetary_value,
    ROUND(AVG(avg_order_value), 2) AS avg_order_value
FROM customer_segments
GROUP BY customer_segment
ORDER BY avg_monetary_value DESC;

-- Query 5: Inventory analysis with stock turnover and reorder points
-- Performance: Complex calculations with window functions
WITH product_metrics AS (
    SELECT 
        p.product_id,
        p.name,
        p.brand,
        p.stock_quantity,
        p.base_price,
        COALESCE(SUM(oi.quantity), 0) AS total_sold,
        COALESCE(COUNT(DISTINCT o.order_id), 0) AS orders_containing_product,
        COALESCE(AVG(oi.quantity), 0) AS avg_quantity_per_order,
        MIN(o.created_at) AS first_sale_date,
        MAX(o.created_at) AS last_sale_date
    FROM products p
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'delivered'
    WHERE p.is_active = true
    GROUP BY p.product_id, p.name, p.brand, p.stock_quantity, p.base_price
),
inventory_analysis AS (
    SELECT 
        *,
        CASE 
            WHEN first_sale_date IS NOT NULL 
            THEN total_sold / GREATEST(EXTRACT(DAYS FROM (CURRENT_DATE - first_sale_date::date)), 1) * 30
            ELSE 0 
        END AS monthly_turnover_rate,
        CASE 
            WHEN total_sold > 0 
            THEN stock_quantity / (total_sold / GREATEST(EXTRACT(DAYS FROM (CURRENT_DATE - first_sale_date::date)), 1))
            ELSE 999 
        END AS days_of_inventory,
        base_price * stock_quantity AS inventory_value
    FROM product_metrics
)
SELECT 
    name,
    brand,
    stock_quantity,
    total_sold,
    ROUND(monthly_turnover_rate, 2) AS monthly_turnover,
    ROUND(days_of_inventory, 1) AS days_of_inventory,
    ROUND(inventory_value, 2) AS inventory_value,
    CASE 
        WHEN days_of_inventory < 7 THEN 'URGENT REORDER'
        WHEN days_of_inventory < 14 THEN 'REORDER SOON'
        WHEN days_of_inventory < 30 THEN 'MONITOR'
        WHEN days_of_inventory > 90 THEN 'OVERSTOCK'
        ELSE 'NORMAL'
    END AS inventory_status,
    CASE 
        WHEN monthly_turnover_rate > 0 
        THEN CEIL(monthly_turnover_rate * 1.5)  -- 1.5 months safety stock
        ELSE stock_quantity 
    END AS suggested_reorder_point
FROM inventory_analysis
ORDER BY days_of_inventory ASC, inventory_value DESC;

-- Query 6: Customer lifetime value prediction with cohort analysis
-- Performance: Complex cohort analysis with multiple CTEs
WITH first_purchase AS (
    SELECT 
        user_id,
        MIN(created_at::date) AS first_purchase_date,
        DATE_TRUNC('month', MIN(created_at)) AS cohort_month
    FROM orders 
    WHERE order_status = 'delivered'
    GROUP BY user_id
),
customer_orders AS (
    SELECT 
        fp.user_id,
        fp.first_purchase_date,
        fp.cohort_month,
        o.created_at::date AS order_date,
        DATE_TRUNC('month', o.created_at) AS order_month,
        o.final_amount,
        EXTRACT(EPOCH FROM (DATE_TRUNC('month', o.created_at) - fp.cohort_month)) / (30.44 * 24 * 60 * 60) AS period_number
    FROM first_purchase fp
    JOIN orders o ON fp.user_id = o.user_id
    WHERE o.order_status = 'delivered'
),
cohort_data AS (
    SELECT 
        cohort_month,
        period_number,
        COUNT(DISTINCT user_id) AS customers,
        SUM(final_amount) AS revenue,
        AVG(final_amount) AS avg_order_value,
        SUM(SUM(final_amount)) OVER (
            PARTITION BY user_id 
            ORDER BY period_number 
            ROWS UNBOUNDED PRECEDING
        ) / COUNT(DISTINCT user_id) AS cumulative_clv
    FROM customer_orders
    GROUP BY cohort_month, period_number
),
retention_rates AS (
    SELECT 
        cohort_month,
        period_number,
        customers,
        revenue,
        ROUND(avg_order_value, 2) AS avg_order_value,
        FIRST_VALUE(customers) OVER (
            PARTITION BY cohort_month 
            ORDER BY period_number
        ) AS cohort_size,
        ROUND(customers::float / FIRST_VALUE(customers) OVER (
            PARTITION BY cohort_month 
            ORDER BY period_number
        ) * 100, 1) AS retention_rate
    FROM cohort_data
)
SELECT 
    cohort_month,
    cohort_size,
    period_number,
    customers,
    retention_rate,
    ROUND(revenue, 2) AS period_revenue,
    avg_order_value,
    ROUND(revenue / cohort_size, 2) AS revenue_per_initial_customer
FROM retention_rates
WHERE period_number <= 12  -- First 12 months
ORDER BY cohort_month, period_number;

-- Query 7: Geographic sales distribution and performance
-- Performance: JSON operations and geographic analysis
WITH geographic_sales AS (
    SELECT 
        o.shipping_address->>'country' AS country,
        o.shipping_address->>'state' AS state,
        o.shipping_address->>'city' AS city,
        COUNT(*) AS order_count,
        SUM(o.final_amount) AS total_revenue,
        AVG(o.final_amount) AS avg_order_value,
        COUNT(DISTINCT o.user_id) AS unique_customers
    FROM orders o
    WHERE o.order_status = 'delivered' 
    AND o.shipping_address IS NOT NULL
    GROUP BY o.shipping_address->>'country', o.shipping_address->>'state', o.shipping_address->>'city'
),
country_totals AS (
    SELECT 
        country,
        SUM(order_count) AS country_orders,
        SUM(total_revenue) AS country_revenue,
        COUNT(DISTINCT state) AS states_count,
        COUNT(DISTINCT city) AS cities_count
    FROM geographic_sales
    GROUP BY country
)
SELECT 
    gs.country,
    gs.state,
    gs.city,
    gs.order_count,
    ROUND(gs.total_revenue, 2) AS total_revenue,
    ROUND(gs.avg_order_value, 2) AS avg_order_value,
    gs.unique_customers,
    ct.country_orders,
    ct.country_revenue,
    ROUND((gs.total_revenue / ct.country_revenue * 100), 2) AS pct_of_country_revenue,
    RANK() OVER (PARTITION BY gs.country ORDER BY gs.total_revenue DESC) AS city_rank_in_country
FROM geographic_sales gs
JOIN country_totals ct ON gs.country = ct.country
WHERE gs.order_count >= 10  -- Only cities with significant volume
ORDER BY ct.country_revenue DESC, gs.total_revenue DESC;

-- Query 8: Product recommendation based on collaborative filtering
-- Performance: Complex similarity calculations
WITH user_product_matrix AS (
    SELECT 
        o.user_id,
        oi.product_id,
        SUM(oi.quantity) AS total_quantity,
        COUNT(*) AS purchase_frequency,
        SUM(oi.total_price) AS total_spent
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.user_id, oi.product_id
),
user_similarities AS (
    SELECT 
        u1.user_id AS user1,
        u2.user_id AS user2,
        COUNT(*) AS common_products,
        CORR(u1.total_quantity, u2.total_quantity) AS quantity_correlation
    FROM user_product_matrix u1
    JOIN user_product_matrix u2 ON u1.product_id = u2.product_id AND u1.user_id < u2.user_id
    GROUP BY u1.user_id, u2.user_id
    HAVING COUNT(*) >= 3 AND CORR(u1.total_quantity, u2.total_quantity) > 0.5
),
product_recommendations AS (
    SELECT 
        us.user1 AS target_user,
        upm2.product_id AS recommended_product,
        p.name AS product_name,
        p.brand,
        AVG(us.quantity_correlation) AS avg_similarity,
        COUNT(*) AS recommendation_strength,
        AVG(upm2.total_quantity) AS avg_quantity_by_similar_users
    FROM user_similarities us
    JOIN user_product_matrix upm2 ON us.user2 = upm2.user_id
    JOIN products p ON upm2.product_id = p.product_id
    WHERE NOT EXISTS (
        SELECT 1 FROM user_product_matrix upm1 
        WHERE upm1.user_id = us.user1 AND upm1.product_id = upm2.product_id
    )
    GROUP BY us.user1, upm2.product_id, p.name, p.brand
    HAVING COUNT(*) >= 2
)
SELECT 
    target_user,
    recommended_product,
    product_name,
    brand,
    ROUND(avg_similarity, 3) AS similarity_score,
    recommendation_strength,
    ROUND(avg_quantity_by_similar_users, 1) AS expected_quantity,
    ROW_NUMBER() OVER (PARTITION BY target_user ORDER BY avg_similarity DESC, recommendation_strength DESC) AS recommendation_rank
FROM product_recommendations
WHERE recommendation_rank <= 5  -- Top 5 recommendations per user
ORDER BY target_user, recommendation_rank;

-- Query 9: Seasonal trends and forecasting
-- Performance: Time series analysis with seasonal decomposition
WITH daily_sales AS (
    SELECT 
        created_at::date AS sale_date,
        COUNT(*) AS order_count,
        SUM(final_amount) AS daily_revenue,
        EXTRACT(DOW FROM created_at) AS day_of_week,
        EXTRACT(MONTH FROM created_at) AS month,
        EXTRACT(QUARTER FROM created_at) AS quarter
    FROM orders 
    WHERE order_status = 'delivered'
    GROUP BY created_at::date
),
seasonal_analysis AS (
    SELECT 
        *,
        AVG(daily_revenue) OVER (
            ORDER BY sale_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS ma_7_day,
        AVG(daily_revenue) OVER (
            ORDER BY sale_date 
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS ma_30_day,
        LAG(daily_revenue, 7) OVER (ORDER BY sale_date) AS prev_week_revenue,
        LAG(daily_revenue, 365) OVER (ORDER BY sale_date) AS prev_year_revenue
    FROM daily_sales
),
trend_analysis AS (
    SELECT 
        *,
        CASE 
            WHEN prev_week_revenue IS NOT NULL 
            THEN ROUND(((daily_revenue - prev_week_revenue) / prev_week_revenue * 100), 2)
            ELSE NULL 
        END AS wow_growth,
        CASE 
            WHEN prev_year_revenue IS NOT NULL 
            THEN ROUND(((daily_revenue - prev_year_revenue) / prev_year_revenue * 100), 2)
            ELSE NULL 
        END AS yoy_growth,
        daily_revenue - ma_30_day AS trend_deviation
    FROM seasonal_analysis
)
SELECT 
    month,
    quarter,
    day_of_week,
    CASE day_of_week 
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_name,
    COUNT(*) AS days_count,
    ROUND(AVG(daily_revenue), 2) AS avg_daily_revenue,
    ROUND(AVG(order_count), 1) AS avg_daily_orders,
    ROUND(STDDEV(daily_revenue), 2) AS revenue_volatility,
    ROUND(AVG(wow_growth), 2) AS avg_wow_growth,
    ROUND(AVG(yoy_growth), 2) AS avg_yoy_growth
FROM trend_analysis
WHERE sale_date >= CURRENT_DATE - INTERVAL '2 years'
GROUP BY month, quarter, day_of_week
ORDER BY quarter, month, day_of_week;

-- Query 10: Advanced fraud detection patterns
-- Performance: Pattern matching and anomaly detection
WITH order_patterns AS (
    SELECT 
        o.user_id,
        o.order_id,
        o.created_at,
        o.final_amount,
        o.shipping_address,
        o.billing_address,
        COUNT(*) OVER (
            PARTITION BY o.user_id 
            ORDER BY o.created_at 
            RANGE BETWEEN INTERVAL '1 hour' PRECEDING AND CURRENT ROW
        ) AS orders_last_hour,
        COUNT(*) OVER (
            PARTITION BY o.user_id 
            ORDER BY o.created_at 
            RANGE BETWEEN INTERVAL '1 day' PRECEDING AND CURRENT ROW
        ) AS orders_last_day,
        AVG(o.final_amount) OVER (
            PARTITION BY o.user_id 
            ORDER BY o.created_at 
            ROWS BETWEEN 10 PRECEDING AND 1 PRECEDING
        ) AS avg_previous_orders,
        o.shipping_address->>'city' = o.billing_address->>'city' AS same_city,
        o.shipping_address->>'country' = o.billing_address->>'country' AS same_country
    FROM orders o
    WHERE o.created_at >= CURRENT_DATE - INTERVAL '30 days'
),
risk_scoring AS (
    SELECT 
        *,
        CASE 
            WHEN orders_last_hour > 3 THEN 25
            WHEN orders_last_hour > 1 THEN 10
            ELSE 0
        END +
        CASE 
            WHEN orders_last_day > 10 THEN 30
            WHEN orders_last_day > 5 THEN 15
            ELSE 0
        END +
        CASE 
            WHEN avg_previous_orders IS NOT NULL AND final_amount > avg_previous_orders * 5 THEN 20
            WHEN avg_previous_orders IS NOT NULL AND final_amount > avg_previous_orders * 3 THEN 10
            ELSE 0
        END +
        CASE 
            WHEN NOT same_country THEN 15
            WHEN NOT same_city THEN 5
            ELSE 0
        END AS risk_score
    FROM order_patterns
)
SELECT 
    user_id,
    order_id,
    created_at,
    final_amount,
    orders_last_hour,
    orders_last_day,
    ROUND(avg_previous_orders, 2) AS avg_previous_orders,
    same_city,
    same_country,
    risk_score,
    CASE 
        WHEN risk_score >= 60 THEN 'HIGH RISK'
        WHEN risk_score >= 30 THEN 'MEDIUM RISK'
        WHEN risk_score >= 15 THEN 'LOW RISK'
        ELSE 'NORMAL'
    END AS risk_level
FROM risk_scoring
WHERE risk_score > 0
ORDER BY risk_score DESC, created_at DESC;

-- Create Stored Procedures and Functions

-- Function 1: Calculate customer lifetime value
CREATE OR REPLACE FUNCTION calculate_customer_ltv(customer_id UUID, prediction_months INTEGER DEFAULT 12)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    avg_monthly_value DECIMAL(10,2);
    avg_monthly_orders DECIMAL(10,2);
    months_active INTEGER;
    predicted_ltv DECIMAL(10,2);
BEGIN
    -- Calculate historical metrics
    SELECT 
        COALESCE(AVG(monthly_revenue), 0),
        COALESCE(AVG(monthly_orders), 0),
        COALESCE(COUNT(DISTINCT month_year), 1)
    INTO avg_monthly_value, avg_monthly_orders, months_active
    FROM (
        SELECT 
            DATE_TRUNC('month', created_at) AS month_year,
            SUM(final_amount) AS monthly_revenue,
            COUNT(*) AS monthly_orders
        FROM orders 
        WHERE user_id = customer_id 
        AND order_status = 'delivered'
        GROUP BY DATE_TRUNC('month', created_at)
    ) monthly_stats;
    
    -- Simple LTV prediction based on historical average
    predicted_ltv := avg_monthly_value * prediction_months;
    
    RETURN predicted_ltv;
END;
$$ LANGUAGE plpgsql;

-- Function 2: Get product performance score
CREATE OR REPLACE FUNCTION get_product_performance_score(product_uuid UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'product_id', p.product_id,
        'name', p.name,
        'total_sold', COALESCE(SUM(oi.quantity), 0),
        'total_revenue', COALESCE(SUM(oi.total_price), 0),
        'avg_rating', 4.2, -- Placeholder since we don't have ratings table
        'performance_score', 
            CASE 
                WHEN COALESCE(SUM(oi.quantity), 0) > 100 THEN 'HIGH'
                WHEN COALESCE(SUM(oi.quantity), 0) > 50 THEN 'MEDIUM'
                ELSE 'LOW'
            END,
        'last_sold', MAX(o.created_at)
    )
    INTO result
    FROM products p
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'delivered'
    WHERE p.product_id = product_uuid
    GROUP BY p.product_id, p.name;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Stored Procedure: Update inventory based on sales velocity
CREATE OR REPLACE PROCEDURE update_inventory_alerts()
LANGUAGE plpgsql AS $$
DECLARE
    product_record RECORD;
    reorder_point INTEGER;
BEGIN
    FOR product_record IN 
        SELECT 
            p.product_id,
            p.name,
            p.stock_quantity,
            COALESCE(SUM(oi.quantity), 0) AS total_sold_30d
        FROM products p
        LEFT JOIN order_items oi ON p.product_id = oi.product_id
        LEFT JOIN orders o ON oi.order_id = o.order_id 
        WHERE o.created_at >= CURRENT_DATE - INTERVAL '30 days'
        AND o.order_status = 'delivered'
        GROUP BY p.product_id, p.name, p.stock_quantity
    LOOP
        -- Calculate reorder point (30-day sales + 50% buffer)
        reorder_point := CEIL(product_record.total_sold_30d * 1.5);
        
        -- Create notification if stock is below reorder point
        IF product_record.stock_quantity <= reorder_point THEN
            INSERT INTO notifications (user_id, title, message, notification_type, priority)
            SELECT 
                u.user_id,
                'Low Stock Alert',
                'Product "' || product_record.name || '" is running low. Current stock: ' || 
                product_record.stock_quantity || ', Reorder point: ' || reorder_point,
                'inventory',
                CASE 
                    WHEN product_record.stock_quantity = 0 THEN 'urgent'
                    WHEN product_record.stock_quantity <= reorder_point * 0.5 THEN 'high'
                    ELSE 'normal'
                END
            FROM users u 
            WHERE u.role IN ('admin', 'staff');
        END IF;
    END LOOP;
    
    RAISE NOTICE 'Inventory alerts updated successfully';
END;
$$;

-- Query 11: Advanced search with full-text search simulation
-- Performance: Text search and ranking
SELECT 
    p.product_id,
    p.name,
    p.brand,
    p.description,
    p.base_price,
    p.stock_quantity,
    c.name AS category_name,
    -- Simulate relevance score
    (
        CASE WHEN LOWER(p.name) LIKE LOWER('%smartphone%') THEN 10 ELSE 0 END +
        CASE WHEN LOWER(p.description) LIKE LOWER('%smartphone%') THEN 5 ELSE 0 END +
        CASE WHEN LOWER(p.brand) LIKE LOWER('%apple%') THEN 8 ELSE 0 END +
        CASE WHEN p.stock_quantity > 0 THEN 2 ELSE 0 END
    ) AS relevance_score,
    COALESCE(sales_stats.total_sold, 0) AS popularity_score
FROM products p
JOIN categories c ON p.category_id = c.category_id
LEFT JOIN (
    SELECT 
        oi.product_id,
        COUNT(*) AS total_sold
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi.product_id
) sales_stats ON p.product_id = sales_stats.product_id
WHERE 
    (LOWER(p.name) LIKE LOWER('%smartphone%') OR 
     LOWER(p.description) LIKE LOWER('%smartphone%') OR
     LOWER(p.brand) LIKE LOWER('%apple%'))
    AND p.is_active = true
ORDER BY relevance_score DESC, popularity_score DESC, p.base_price ASC
LIMIT 20;

-- Query 12: Cart abandonment analysis
-- Performance: Complex time-based analysis
WITH cart_analysis AS (
    SELECT 
        c.cart_id,
        c.user_id,
        c.created_at AS cart_created,
        c.updated_at AS cart_updated,
        COUNT(ci.cart_item_id) AS items_count,
        SUM(ci.price * ci.quantity) AS cart_value,
        MAX(ci.added_at) AS last_item_added,
        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - c.updated_at)) / 3600 AS hours_since_update
    FROM cart c
    LEFT JOIN cart_items ci ON c.cart_id = ci.cart_id
    GROUP BY c.cart_id, c.user_id, c.created_at, c.updated_at
),
user_orders AS (
    SELECT 
        user_id,
        MAX(created_at) AS last_order_date,
        COUNT(*) AS total_orders
    FROM orders
    WHERE order_status IN ('delivered', 'shipped', 'processing')
    GROUP BY user_id
)
SELECT 
    ca.user_id,
    u.first_name || ' ' || u.last_name AS customer_name,
    u.email,
    ca.items_count,
    ROUND(ca.cart_value, 2) AS cart_value,
    ca.last_item_added,
    ROUND(ca.hours_since_update, 1) AS hours_since_update,
    COALESCE(uo.total_orders, 0) AS previous_orders,
    COALESCE(uo.last_order_date, '1900-01-01'::timestamp) AS last_order_date,
    CASE 
        WHEN ca.hours_since_update < 1 THEN 'ACTIVE'
        WHEN ca.hours_since_update < 24 THEN 'RECENT'
        WHEN ca.hours_since_update < 72 THEN 'ABANDONED'
        ELSE 'COLD'
    END AS cart_status,
    CASE 
        WHEN ca.cart_value > 100 AND ca.hours_since_update BETWEEN 24 AND 72 THEN 'HIGH_VALUE_RECOVERY'
        WHEN COALESCE(uo.total_orders, 0) > 0 AND ca.hours_since_update BETWEEN 12 AND 48 THEN 'RETURNING_CUSTOMER_NUDGE'
        WHEN COALESCE(uo.total_orders, 0) = 0 AND ca.hours_since_update BETWEEN 6 AND 24 THEN 'FIRST_TIME_ENCOURAGEMENT'
        ELSE 'NO_ACTION'
    END AS recovery_strategy
FROM cart_analysis ca
JOIN users u ON ca.user_id = u.user_id
LEFT JOIN user_orders uo ON ca.user_id = uo.user_id
WHERE ca.items_count > 0 
AND ca.hours_since_update > 1
ORDER BY ca.cart_value DESC, ca.hours_since_update ASC;

-- Query 13: Supplier/Brand performance analysis
-- Performance: Comprehensive supplier metrics
WITH brand_performance AS (
    SELECT 
        p.brand,
        COUNT(DISTINCT p.product_id) AS product_count,
        SUM(p.stock_quantity) AS total_inventory,
        SUM(p.base_price * p.stock_quantity) AS inventory_value,
        COALESCE(SUM(sales.units_sold), 0) AS total_units_sold,
        COALESCE(SUM(sales.revenue), 0) AS total_revenue,
        COALESCE(AVG(sales.avg_selling_price), 0) AS avg_selling_price,
        COUNT(DISTINCT sales.customer_count) AS unique_customers
    FROM products p
    LEFT JOIN (
        SELECT 
            oi.product_id,
            SUM(oi.quantity) AS units_sold,
            SUM(oi.total_price) AS revenue,
            AVG(oi.unit_price) AS avg_selling_price,
            COUNT(DISTINCT o.user_id) AS customer_count
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_status = 'delivered'
        AND o.created_at >= CURRENT_DATE - INTERVAL '12 months'
        GROUP BY oi.product_id
    ) sales ON p.product_id = sales.product_id
    WHERE p.brand IS NOT NULL
    GROUP BY p.brand
),
brand_rankings AS (
    SELECT 
        *,
        RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
        RANK() OVER (ORDER BY total_units_sold DESC) AS volume_rank,
        RANK() OVER (ORDER BY avg_selling_price DESC) AS price_rank,
        CASE 
            WHEN total_units_sold > 0 
            THEN ROUND((total_revenue / inventory_value * 100), 2)
            ELSE 0 
        END AS inventory_turnover_pct
    FROM brand_performance
)
SELECT 
    brand,
    product_count,
    total_inventory,
    ROUND(inventory_value, 2) AS inventory_value,
    total_units_sold,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(avg_selling_price, 2) AS avg_selling_price,
    unique_customers,
    revenue_rank,
    volume_rank,
    price_rank,
    inventory_turnover_pct,
    CASE 
        WHEN revenue_rank <= 5 AND volume_rank <= 5 THEN 'TOP_PERFORMER'
        WHEN revenue_rank <= 10 OR volume_rank <= 10 THEN 'GOOD_PERFORMER'
        WHEN inventory_turnover_pct < 10 THEN 'UNDERPERFORMER'
        ELSE 'AVERAGE'
    END AS performance_category
FROM brand_rankings
WHERE total_revenue > 0
ORDER BY total_revenue DESC;

-- Query 14: Dynamic pricing optimization analysis
-- Performance: Price elasticity and optimization calculations
WITH price_elasticity AS (
    SELECT 
        p.product_id,
        p.name,
        p.brand,
        p.base_price,
        AVG(oi.unit_price) AS avg_selling_price,
        STDDEV(oi.unit_price) AS price_volatility,
        SUM(oi.quantity) AS total_sold,
        COUNT(DISTINCT oi.order_id) AS order_frequency,
        MIN(oi.unit_price) AS min_selling_price,
        MAX(oi.unit_price) AS max_selling_price,
        -- Calculate price elasticity approximation
        CASE 
            WHEN STDDEV(oi.unit_price) > 0 AND AVG(oi.quantity) > 0
            THEN (STDDEV(oi.quantity) / AVG(oi.quantity)) / (STDDEV(oi.unit_price) / AVG(oi.unit_price))
            ELSE 0
        END AS price_elasticity
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    AND o.created_at >= CURRENT_DATE - INTERVAL '6 months'
    GROUP BY p.product_id, p.name, p.brand, p.base_price
    HAVING COUNT(*) >= 10  -- Minimum sample size
),
competitor_analysis AS (
    SELECT 
        brand,
        AVG(base_price) AS avg_brand_price,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY base_price) AS median_brand_price
    FROM products 
    WHERE is_active = true
    GROUP BY brand
)
SELECT 
    pe.product_id,
    pe.name,
    pe.brand,
    ROUND(pe.base_price, 2) AS current_price,
    ROUND(pe.avg_selling_price, 2) AS avg_selling_price,
    ROUND(pe.price_volatility, 2) AS price_volatility,
    pe.total_sold,
    ROUND(pe.price_elasticity, 3) AS price_elasticity,
    ROUND(ca.avg_brand_price, 2) AS avg_brand_price,
    ROUND(ca.median_brand_price, 2) AS median_brand_price,
    -- Price optimization suggestions
    CASE 
        WHEN pe.price_elasticity < -1 THEN 'DECREASE_PRICE'  -- Elastic demand
        WHEN pe.price_elasticity > -0.5 THEN 'INCREASE_PRICE'  -- Inelastic demand
        WHEN pe.base_price < ca.avg_brand_price * 0.8 THEN 'INCREASE_PRICE'
        WHEN pe.base_price > ca.avg_brand_price * 1.2 THEN 'DECREASE_PRICE'
        ELSE 'MAINTAIN_PRICE'
    END AS pricing_recommendation,
    -- Suggested optimal price
    ROUND(
        CASE 
            WHEN pe.price_elasticity < -1 THEN pe.base_price * 0.95
            WHEN pe.price_elasticity > -0.5 THEN pe.base_price * 1.05
            WHEN pe.base_price < ca.avg_brand_price * 0.8 THEN ca.avg_brand_price * 0.9
            WHEN pe.base_price > ca.avg_brand_price * 1.2 THEN ca.avg_brand_price * 1.1
            ELSE pe.base_price
        END, 2
    ) AS suggested_price,
    ROUND((pe.avg_selling_price - pe.base_price) / pe.base_price * 100, 2) AS margin_pct
FROM price_elasticity pe
JOIN competitor_analysis ca ON pe.brand = ca.brand
ORDER BY pe.total_sold DESC, ABS(pe.price_elasticity) DESC;

-- Query 15: Advanced customer journey analysis
-- Performance: Complex customer behavior tracking
WITH customer_touchpoints AS (
    SELECT 
        user_id,
        'registration' AS touchpoint_type,
        created_at AS touchpoint_time,
        0 AS monetary_value,
        1 AS sequence_number
    FROM users
    
    UNION ALL
    
    SELECT 
        user_id,
        'cart_creation' AS touchpoint_type,
        created_at AS touchpoint_time,
        0 AS monetary_value,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) + 1000 AS sequence_number
    FROM cart
    
    UNION ALL
    
    SELECT 
        user_id,
        'order_placed' AS touchpoint_type,
        created_at AS touchpoint_time,
        final_amount AS monetary_value,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) + 2000 AS sequence_number
    FROM orders
    
    UNION ALL
    
    SELECT 
        f.user_id,
        'product_favorited' AS touchpoint_type,
        f.added_at AS touchpoint_time,
        0 AS monetary_value,
        ROW_NUMBER() OVER (PARTITION BY f.user_id ORDER BY f.added_at) + 3000 AS sequence_number
    FROM favorites f
),
customer_journeys AS (
    SELECT 
        user_id,
        touchpoint_type,
        touchpoint_time,
        monetary_value,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY touchpoint_time) AS journey_step,
        LAG(touchpoint_type) OVER (PARTITION BY user_id ORDER BY touchpoint_time) AS prev_touchpoint,
        LAG(touchpoint_time) OVER (PARTITION BY user_id ORDER BY touchpoint_time) AS prev_touchpoint_time,
        LEAD(touchpoint_type) OVER (PARTITION BY user_id ORDER BY touchpoint_time) AS next_touchpoint,
        EXTRACT(EPOCH FROM (touchpoint_time - LAG(touchpoint_time) OVER (PARTITION BY user_id ORDER BY touchpoint_time))) / 3600 AS hours_since_prev
    FROM customer_touchpoints
),
journey_patterns AS (
    SELECT 
        prev_touchpoint || ' -> ' || touchpoint_type AS journey_pattern,
        COUNT(*) AS pattern_frequency,
        AVG(hours_since_prev) AS avg_time_between,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY hours_since_prev) AS median_time_between,
        AVG(monetary_value) FILTER (WHERE monetary_value > 0) AS avg_conversion_value,
        COUNT(*) FILTER (WHERE monetary_value > 0) AS conversions,
        COUNT(*) AS total_transitions
    FROM customer_journeys
    WHERE prev_touchpoint IS NOT NULL
    GROUP BY prev_touchpoint || ' -> ' || touchpoint_type
),
customer_journey_summary AS (
    SELECT 
        cj.user_id,
        u.first_name || ' ' || u.last_name AS customer_name,
        MIN(cj.touchpoint_time) AS first_interaction,
        MAX(cj.touchpoint_time) AS last_interaction,
        COUNT(DISTINCT cj.touchpoint_type) AS touchpoint_variety,
        COUNT(*) AS total_touchpoints,
        SUM(cj.monetary_value) AS total_value,
        COUNT(*) FILTER (WHERE cj.touchpoint_type = 'order_placed') AS total_orders,
        EXTRACT(DAYS FROM (MAX(cj.touchpoint_time) - MIN(cj.touchpoint_time))) AS customer_lifespan_days
    FROM customer_journeys cj
    JOIN users u ON cj.user_id = u.user_id
    GROUP BY cj.user_id, u.first_name, u.last_name
)
SELECT 
    jp.journey_pattern,
    jp.pattern_frequency,
    ROUND(jp.avg_time_between, 2) AS avg_hours_between,
    ROUND(jp.median_time_between, 2) AS median_hours_between,
    ROUND(jp.avg_conversion_value, 2) AS avg_conversion_value,
    jp.conversions,
    ROUND((jp.conversions::float / jp.total_transitions * 100), 2) AS conversion_rate_pct,
    CASE 
        WHEN jp.journey_pattern LIKE '%order_placed' THEN 'CONVERSION_PATH'
        WHEN jp.journey_pattern LIKE '%cart_creation%' THEN 'CONSIDERATION_PATH'
        WHEN jp.journey_pattern LIKE '%product_favorited%' THEN 'ENGAGEMENT_PATH'
        ELSE 'OTHER_PATH'
    END AS path_category
FROM journey_patterns jp
WHERE jp.pattern_frequency >= 100  -- Only patterns with significant volume
ORDER BY jp.pattern_frequency DESC, jp.avg_conversion_value DESC;

-- Create index suggestions for optimal performance
-- These indexes should significantly improve query performance

-- Indexes for user-related queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_user_status_created 
ON orders(user_id, order_status, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_order_items_product_order 
ON order_items(product_id, order_id);

-- Indexes for product performance queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_category_active_created 
ON products(category_id, is_active, created_at);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_brand_price 
ON products(brand, base_price) WHERE is_active = true;

-- Indexes for time-based analytics
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_created_status_amount 
ON orders(created_at, order_status, final_amount);

-- Indexes for geographic analysis
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_shipping_country 
ON orders USING GIN ((shipping_address->>'country'));

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_shipping_state 
ON orders USING GIN ((shipping_address->>'state'));

-- Indexes for notification queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_user_read_created 
ON notifications(user_id, is_read, created_at DESC);

-- Indexes for cart analysis
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cart_items_cart_added 
ON cart_items(cart_id, added_at);

-- Composite indexes for complex queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_user_created_status_amount 
ON orders(user_id, created_at, order_status, final_amount);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_category_brand_price_stock 
ON products(category_id, brand, base_price, stock_quantity) 
WHERE is_active = true;
