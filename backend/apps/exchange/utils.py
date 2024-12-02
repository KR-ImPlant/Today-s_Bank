import requests
import certifi
from datetime import datetime
from datetime import timedelta
from .models import ExchangeRate

def get_exchange_rates(authkey):
    url = "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON"
    today = datetime.now()
    
    # 오늘부터 최대 5일 전까지 데이터 확인
    for i in range(5):
        check_date = today - timedelta(days=i)
        if check_date.weekday() >= 5:  # 주말이면 건너뛰기
            continue
            
        params = {
            "authkey": authkey,
            "searchdate": check_date.strftime("%Y%m%d"),
            "data": "AP01"
        }
        
        try:
            response = requests.get(url, params=params, verify=False)
            data = response.json()
            
            if isinstance(data, list) and data:
                return {"RESULT": 1, "list": data}
                
        except Exception as e:
            print(f"Error fetching data for {check_date}: {str(e)}")
            continue
    
    return {"RESULT": 2, "message": "No valid data found in the last 5 days"}

def get_historical_rates(authkey, currency_code, days=7):
    # SSL 경고 무시 (개발 환경용)
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # DB에서 기존 데이터 조회
    existing_rates = ExchangeRate.objects.filter(
        currency_code=currency_code,
        date__range=[start_date, end_date]
    ).order_by('date')
    
    if existing_rates.exists():
        return [
            {
                'date': rate.date.strftime('%Y-%m-%d'),
                'rate': float(rate.rate),
                'currency_code': currency_code,
            } for rate in existing_rates
        ]
    
    # API로 데이터 조회 및 저장
    rates = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # 주말 제외
            try:
                response = requests.get(
                    "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON",
                    params={
                        "authkey": authkey,
                        "searchdate": current_date.strftime("%Y%m%d"),
                        "data": "AP01"
                    },
                    verify=False  # SSL 검증 비활성화
                )
                data = response.json()
                
                if isinstance(data, list):
                    for item in data:
                        if item['cur_unit'] == currency_code:
                            rate = float(item['deal_bas_r'].replace(',', ''))
                            ExchangeRate.objects.create(
                                currency_code=currency_code,
                                rate=rate,
                                date=current_date
                            )
                            rates.append({
                                'date': current_date.strftime('%Y-%m-%d'),
                                'rate': rate
                            })
            except Exception as e:
                print(f"Error fetching data for {current_date}: {str(e)}")
                
        current_date += timedelta(days=1)
    
    return rates

def calculate_cross_rates(from_rates, to_rates):
    rates = []
    
    # 통화별 스케일링 팩터 정의
    SCALE_FACTORS = {
        'BHD': 0.1,    # 바레인 디나르
        'KWD': 0.1,    # 쿠웨이트 디나르
        'JOD': 0.1,    # 요르단 디나르
        'OMR': 0.1,    # 오만 리알
        'KRW': 1000,   # 한국 원
        'VND': 1000,   # 베트남 동
        'IDR': 1000,   # 인도네시아 루피아
        'JPY': 100,    # 일본 엔
    }
    
    from_currency = from_rates[0].get('currency_code', '')
    to_currency = to_rates[0].get('currency_code', '')
    
    # 스케일링 팩터 가져오기
    from_scale = SCALE_FACTORS.get(from_currency, 1)
    to_scale = SCALE_FACTORS.get(to_currency, 1)
    
    for from_rate in from_rates:
        matching_to_rate = next(
            (r for r in to_rates if r['date'] == from_rate['date']), 
            None
        )
        if matching_to_rate:
            if matching_to_rate['rate'] == 0:
                continue
                
            if from_currency == 'KRW':
                # KRW -> 다른 통화
                rate = (from_scale / matching_to_rate['rate']) * (1 / to_scale)
            elif to_currency == 'KRW':
                # 다른 통화 -> KRW
                rate = from_rate['rate'] * (from_scale / to_scale)
            else:
                # 일반 통화 간 환율
                rate = (from_rate['rate'] / matching_to_rate['rate']) * (from_scale / to_scale)
                
            rates.append({
                'date': from_rate['date'],
                'rate': rate
            })
    return rates
