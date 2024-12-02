from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import get_exchange_rates, get_historical_rates, calculate_cross_rates
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import io
import base64

matplotlib.use('Agg')

load_dotenv()

@api_view(["GET"])
def exchange_rates(request):
    authkey = os.environ.get('EXCHANGE_API_KEY')
    print(authkey)
    if not authkey:
        return Response(
            {'error': 'API key not found'}, 
            status=500
        )
    
    result = get_exchange_rates(authkey)
    
    
    if result['RESULT'] == 1:
        return Response(result['list'])
    
    return Response(
        {'error': result.get('message', 'Unknown error')}, 
        status=500
    )

@api_view(["GET"])
def exchange_rates_history(request):
    from_currency = request.GET.get('from')
    to_currency = request.GET.get('to')
    days = int(request.GET.get('days', 7))
    
    authkey = os.environ.get('EXCHANGE_API_KEY')
    if not authkey:
        return Response({'error': 'API key not found'}, status=500)
    
    # KRW로의 환율은 항상 1
    if to_currency == 'KRW':
        rates = get_historical_rates(authkey, from_currency, days)
    else:
        from_rates = get_historical_rates(authkey, from_currency, days)
        to_rates = get_historical_rates(authkey, to_currency, days)
        rates = calculate_cross_rates(from_rates, to_rates)
    
    return Response(rates)

@api_view(["GET"])
def exchange_rate_chart(request):
    from_currency = request.GET.get('from')
    to_currency = request.GET.get('to')
    days = int(request.GET.get('days', 7))
    
    authkey = os.environ.get('EXCHANGE_API_KEY')
    if not authkey:
        return Response({'error': 'API key not found'}, status=500)
    
    try:
        # 환율 데이터 조회
        if to_currency == 'KRW':
            rates = get_historical_rates(authkey, from_currency, days)
        else:
            from_rates = get_historical_rates(authkey, from_currency, days)
            to_rates = get_historical_rates(authkey, to_currency, days)
            rates = calculate_cross_rates(from_rates, to_rates)
        
        # 데이터프레임 생성 및 정렬
        df = pd.DataFrame(rates)
        if df.empty:
            return Response({'error': 'No data available'}, status=404)
            
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # 통계 계산
        stats = {
            'dates': df['date'].dt.strftime('%Y-%m-%d').tolist(),
            'rates': df['rate'].tolist(),
            'mean': float(df['rate'].mean()),
            'std': float(df['rate'].std()),
            'min': float(df['rate'].min()),
            'max': float(df['rate'].max())
        }
        
        return Response({
            'data': stats
        })
        
    except Exception as e:
        print(f"Error in exchange_rate_chart: {str(e)}")
        return Response({'error': str(e)}, status=500)
