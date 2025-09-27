from rest_framework import serializers
from .models import Product, Order, OrderItem


# note: Using ModelSerializer because it auto-generates fields 
#       based on the model, reducing boilerplate code.
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        #! important: Always define 'fields' explicitly for clarity and security. 
        # Using '__all__' can accidentally expose sensitive fields later.
        fields = (
            "id",
            "name",
            "description",
            "price",
            "stock",
        )  # note: tuple of fields to include in the serialized output

    #! important: Field-level validation should follow the pattern 'validate_<fieldname>'
    # This ensures DRF automatically hooks it into that field’s validation pipeline.
    def validate_price(self, value):
        # note: Business rule - price must always be positive
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    #! important: Instead of serializing the whole product object (nested serializer),
    # we expose only the needed fields (name, price).
    # This avoids bloated JSON responses when orders have many items.
    
    # note: 'source' lets us pull data from related model fields
    product_name = serializers.CharField(source="product.name")
    product_price = serializers.DecimalField(
        max_digits=10,  # note: matches Product.price precision
        decimal_places=2,
        source="product.price"
    )

    class Meta:
        model = OrderItem
        #! important: Include only the essential fields for this serializer.
        # Common mistake: Adding 'product' here will cause nested serialization 
        # unless explicitly controlled.
        fields = (
            "product_name", 
            "product_price", 
            "quantity", 
            "item_subtotal"
        )


class OrderSerializer(serializers.ModelSerializer):
    # note: One order has many order items (reverse relationship)
    # 'items' refers to the related_name="items" on the OrderItem model’s FK to Order.
    #! important: 'many=True' is required because it's a one-to-many relation.
    # 'read_only=True' ensures we don’t accidentally try to create items from this serializer.
    items = OrderItemSerializer(many=True, read_only=True)

    # note: SerializerMethodField is used for computed values
    #! important: Always prefix with 'get_<fieldname>' to implement logic.
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        # note: Access all related order items (reverse relation).
        order_items = obj.items.all()
     
        #! important: Summing item_subtotal here avoids double counting.
        # Make sure 'item_subtotal' is a field or property on OrderItem.
        return sum(item.item_subtotal for item in order_items)

    class Meta:
        model = Order
        fields = (
            "order_id", 
            "created_at", 
            "user", 
            "status", 
            "items", 
            "total_price"
        )
        #! important: Always explicitly include user-related fields only if safe.
        # If exposing user info, consider using a custom User serializer instead of raw FK.


class ProductInfoSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()



#     | বিষয়                  | `serializers.Serializer`                       | `serializers.ModelSerializer`       |
# | --------------------- | ---------------------------------------------- | ----------------------------------- |
# | **মূল ধারণা**           | একদম manual serializer                         | Model ভিত্তিক shortcut serializer   |
# | **Model dependency**  | Model-এর উপর নির্ভর করে না                     | সরাসরি Model-এর সাথে কাজ করে        |
# | **ফিল্ড ডিফাইন**       | প্রতিটা ফিল্ড আলাদা করে লিখতে হয়                   | Model-এর ফিল্ড থেকে অটো জেনারেট হয় |
# | **Validation**        | সব validation নিজে লিখতে হয়                   | Model field এর validation অটো চলে   |
# | **create()/update()** | নিজে লিখতে হয়                                 | DRF অটো জেনারেট করে দেয়            |
# | **ব্যবহারের ক্ষেত্র**       | যখন model নেই / কাস্টম ডেটা serialize করতে হয়  | যখন model-এর সাথে কাজ করতে হয়      |
# | **কোডের পরিমাণ**      | বেশি কোড লাগে                                  | কম কোডে কাজ হয়ে যায়               |
