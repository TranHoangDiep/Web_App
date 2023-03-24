from store.models import Product
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    subcategory = serializers.CharField(source='subcategory_id')

    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.price_origin = validated_data.get('price_origin', instance.price_origin)
        instance.image = validated_data.get('image', instance.image)
        instance.content = validated_data.get('content', instance.content)
        instance.public_day = validated_data.get('public_day', instance.public_day)
        instance.viewed = validated_data.get('viewed', instance.viewed)
        instance.save()
        return instance

    def destroy(self, instance):
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
