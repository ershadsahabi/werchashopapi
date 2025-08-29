from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .serializers import OrderCreateSerializer, OrderOutSerializer, LastAddressOutSerializer
from .models import Order


class OrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = OrderCreateSerializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        order = ser.save()
        out = OrderOutSerializer(order)
        return Response(out.data, status=status.HTTP_201_CREATED)
    
# ↓↓↓ جدید
class LastAddressView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        last = Order.objects.filter(user=request.user).order_by('-created_at').first()
        if not last:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response(LastAddressOutSerializer(last).data)