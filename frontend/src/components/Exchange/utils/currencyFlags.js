const currencyToCountry = {
  'KRW': 'KR',
  'USD': 'US',
  'EUR': 'EU',
  'JPY': 'JP',
  'CNH': 'CN',
  'HKD': 'HK',
  'TWD': 'TW',
  'GBP': 'GB',
  'AUD': 'AU',
  'CAD': 'CA',
  'CHF': 'CH',
  'SEK': 'SE',
  'NZD': 'NZ',
  'THB': 'TH',
  'SGD': 'SG',
  'AED': 'AE',
  'BHD': 'BH',
  'IDR': 'ID',
  'MYR': 'MY',
  'SAR': 'SA',
  'KWD': 'KW',
  'BND': 'BN',
  'NOK': 'NO',
  'DKK': 'DK'
};

export const getCountryCodeByCurrency = (currencyCode) => {
  // JPY(100)와 같은 형식 처리
  const cleanCurrencyCode = currencyCode.split('(')[0];
  return currencyToCountry[cleanCurrencyCode] || 'UN'; // UN은 기본값
};

export const getFlagByCountryCode = (countryCode) => {
  return `https://flagcdn.com/${countryCode.toLowerCase()}.svg`;
}; 