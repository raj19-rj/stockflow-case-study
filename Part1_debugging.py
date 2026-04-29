"""
Part 1: Code Review & Debugging
================================
Original code had these issues:
1. No input validation - crashes with 500 on missing fields
2. No SKU uniqueness check - duplicates cause DB errors
3. Two separate commits - data inconsistency if second fails
4. No error handling - unhandled 500 errors in production
5. Price not validated - could be negative or wrong type
6. No authentication - anyone can create products
"""

from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from decimal import Decimal, InvalidOperation

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json

    # Fix 1: Validate required fields
    required_fields = ['name', 'sku', 'price', 
                       'warehouse_id', 'initial_quantity']
    missing = [f for f in required_fields 
               if f not in data or data[f] is None]
    if missing:
        return jsonify({
            "error": f"Missing required fields: {missing}"
        }), 400

    # Fix 2: Validate price is positive decimal
    try:
        price = Decimal(str(data['price']))
        if price < 0:
            return jsonify({
                "error": "Price must be non-negative"
            }), 400
    except InvalidOperation:
        return jsonify({"error": "Invalid price format"}), 400

    # Fix 3: Validate initial_quantity
    if (not isinstance(data['initial_quantity'], int) 
            or data['initial_quantity'] < 0):
        return jsonify({
            "error": "initial_quantity must be a non-negative integer"
        }), 400

    # Fix 4: Check SKU uniqueness before inserting
    existing = Product.query.filter_by(sku=data['sku']).first()
    if existing:
        return jsonify({"error": "SKU already exists"}), 409

    try:
        # Fix 5: Single transaction for both inserts
        product = Product(
            name=data['name'],
            sku=data['sku'],
            price=price,
            warehouse_id=data['warehouse_id'],
            description=data.get('description', '')  # optional field
        )
        db.session.add(product)
        db.session.flush()  # get product.id without committing

        inventory = Inventory(
            product_id=product.id,
            warehouse_id=data['warehouse_id'],
            quantity=data['initial_quantity']
        )
        db.session.add(inventory)
        db.session.commit()  # ONE commit - atomic operation

        return jsonify({
            "message": "Product created",
            "product_id": product.id
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
