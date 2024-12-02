from rest_framework import viewsets
from .models import BankBranch
from .serializers import BankBranchSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

class BankBranchViewSet(viewsets.ModelViewSet):
    queryset = BankBranch.objects.all()
    serializer_class = BankBranchSerializer

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        try:
            lat = float(request.query_params.get('lat'))
            lng = float(request.query_params.get('lng'))
            radius = float(request.query_params.get('radius', 1000))

            # FinMapAPI를 통해 실제 은행 지점 데이터 조회.
            branches = FinMapAPI.search_branches(
                lat - radius/111000,  # 위도 1도 = 약 111km
                lng - radius/(111000*cos(radians(lat))),
                lat + radius/111000,
                lng + radius/(111000*cos(radians(lat)))
            )

            # 응답 데이터 가공.
            return Response(branches)

        except Exception as e:
            logger.error(f"Error in nearby branches search: {str(e)}")
            return Response(
                {"error": "서버 오류가 발생했습니다."}, 
                status=500
            )