from rest_framework import serializers

class ExchangeRateSerializer(serializers.Serializer):
    cur_unit = serializers.CharField(source='CUR_UNIT')
    cur_nm = serializers.CharField(source='CUR_NM')
    deal_bas_r = serializers.CharField(source='DEAL_BAS_R')
