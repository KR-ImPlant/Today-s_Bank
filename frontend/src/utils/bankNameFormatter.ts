export const bankNameMap: { [key: string]: string } = {
    '주식회사 케이뱅크': '케이뱅크',
    '주식회사 카카오뱅크': '카카오뱅크',
    '토스뱅크 주식회사': '토스뱅크',
    '농협은행주식회사': '농협은행',
    '한국스탠다드차타드은행': 'SC제일은행',
    '중소기업은행': 'IBK기업은행',
    '한국산업은행': 'KDB산업은행',
    '한국씨티은행': '한국씨티은행',
    '한국저축은행': '저축은행',
    '우리은행': '우리은행',
    '국민은행': '국민은행',
    '신한은행': '신한은행',
    '하나은행': '하나은행',
    '수협은행': '수협은행',
    '부산은행': '부산은행',
    '광주은행': '광주은행',
    '제주은행': '제주은행',
    '전북은행': '전북은행',
    '경남은행': '경남은행'
  };
  
  export const formatBankName = (bankName: string): string => {
    return bankNameMap[bankName] || bankName;
  };

  export const bankNameLogo: { [key: string]: string } = {
    '페퍼저축은행': '/bank-logos/페퍼글씨.png',
    '흥국저축은행': '/bank-logos/흥국글씨.png',
    '다올저축은행': '/bank-logos/다올글씨.png'
  };

  export const formatBankLogo = (bankName: string): string => {
    return bankNameLogo[bankName] || bankName;
  };