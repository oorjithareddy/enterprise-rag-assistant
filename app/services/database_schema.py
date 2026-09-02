TABLE_DESCRIPTIONS = {
    "olist_orders": (
        "One row per order. Contains order status, customer, "
        "purchase, approval, delivery, and estimated delivery dates."
    ),

    "olist_order_items": (
        "Items belonging to orders. Contains product, seller, "
        "price, freight value, and shipping limit information."
    ),

    "olist_products": (
        "Product catalog. Contains product category and physical "
        "product attributes."
    ),

    "olist_customers": (
        "Customer records. Contains customer identity, city, "
        "state, and postal code."
    ),

    "olist_order_payments": (
        "Payment records for orders. An order may have multiple "
        "payment records."
    ),

    "olist_order_reviews": (
        "Customer review records associated with orders. "
        "Contains review score and review text."
    ),

    "olist_sellers": (
        "Seller records. Contains seller location information."
    ),

    "olist_category_translation": (
        "Maps Portuguese product category names to English "
        "product category names."
    ),

    "olist_geolocation": (
        "Geographic information associated with postal code prefixes."
    ),
}


TABLE_RELATIONSHIPS = """
olist_orders.customer_id
    -> olist_customers.customer_id

olist_order_items.order_id
    -> olist_orders.order_id

olist_order_items.product_id
    -> olist_products.product_id

olist_order_items.seller_id
    -> olist_sellers.seller_id

olist_order_payments.order_id
    -> olist_orders.order_id

olist_order_reviews.order_id
    -> olist_orders.order_id

olist_products.product_category_name
    -> olist_category_translation.product_category_name
"""


BUSINESS_RULES = """
Business interpretation rules:

- olist_orders represents orders.
- olist_order_items represents individual items within orders.
- When counting orders after joining olist_order_items, use
  COUNT(DISTINCT order_id) unless the question explicitly asks
  for item count.
- When calculating product sales value, price is the item price
  and freight_value is the freight charge.
- payment_value represents the payment amount recorded for a
  payment record.
- review_score is the customer review score.
- order_status describes the current recorded order status.
- For product category names, use the English translation from
  olist_category_translation when presenting category names.
- Date fields are stored as TEXT in the source database.
- Use SQLite-compatible SQL.
"""