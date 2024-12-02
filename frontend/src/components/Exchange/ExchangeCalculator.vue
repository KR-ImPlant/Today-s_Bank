<template>
  <div>
    <h1 class="exchange-calculator-title"></h1>
    <div v-if="error" class="error">{{ error }}</div>
    <div class="main-container" v-else>
      <!-- 왼쪽 섹션 -->
      <div class="left-section">
        <div class="calculator-wrapper">
          <div class="calculator-container">
            <!-- 왼쪽: 출발 통화 -->
            <div class="currency-section">
              <div class="currency-select">
                <div class="select-with-flag">
                  <img 
                    :src="getCountryFlag(fromCurrency.code)" 
                    :alt="fromCurrency.code"
                    class="currency-flag"
                  />
                  <select id="fromCurrency" v-model="fromCurrency" required>
                    <option 
                      v-for="currency in commonCurrencies" 
                      :key="currency.code" 
                      :value="currency"
                    >
                      {{ currency.name }} ({{ currency.code }})
                    </option>
                  </select>
                </div>
              </div>
              <div class="amount-input">
                <input 
                  type="text" 
                  id="amount" 
                  :value="formatNumber(amount)" 
                  @input="e => amount = e.target.value.replace(/[^0-9]/g, '')" 
                  required 
                  placeholder="금액을 입력하세요"
                />
              </div>
            </div>

            <!-- 중앙: 스위치 버튼 -->
            <div class="switch-section">
              <button class="switch-button" @click="switchCurrencies">
                ⇄
              </button>
            </div>

            <!-- 오른쪽: 도착 통화 -->
            <div class="currency-section">
              <div class="currency-select">
                <div class="select-with-flag">
                  <img 
                    :src="getCountryFlag(toCurrency.code)" 
                    :alt="toCurrency.code"
                    class="currency-flag"
                  />
                  <select id="toCurrency" v-model="toCurrency" required>
                    <option 
                      v-for="currency in commonCurrencies" 
                      :key="currency.code" 
                      :value="currency"
                    >
                      {{ currency.name }} ({{ currency.code }})
                    </option>
                  </select>
                </div>
              </div>
              <div class="amount-input">
                <input 
                  type="text" 
                  id="convertedAmount" 
                  :value="formatNumber(convertedAmount)" 
                  @input="e => convertedAmount = e.target.value.replace(/[^0-9]/g, '')" 
                  required 
                  placeholder="환전 금액"
                />
              </div>
            </div>
          </div>
        </div>
        
        <!-- 계산기 아래 차트 섹션 -->
        <div class="chart-section" v-if="historicalRates.length">
          <h2>지난 7일간 환율 변화</h2>
          <div class="chart-container">
            <canvas ref="chartCanvas"></canvas>
          </div>
          <div class="statistics">
            <div class="stat-item min">
              <div class="stat-label">최저</div>
              <div class="stat-value">{{ formatAmount(statistics.min) }}</div>
            </div>
            <div class="stat-item mean">
              <div class="stat-label">평균</div>
              <div class="stat-value">{{ formatAmount(statistics.mean) }}</div>
            </div>
            <div class="stat-item max">
              <div class="stat-label">최고</div>
              <div class="stat-value">{{ formatAmount(statistics.max) }}</div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from "vue";
import axios from "axios";
import Chart from 'chart.js/auto';
import CrosshairPlugin from 'chartjs-plugin-crosshair';
import { getCountryCodeByCurrency, getFlagByCountryCode } from './utils/currencyFlags';

Chart.register(CrosshairPlugin);  // 플러그인 등록

export default {
  setup() {
    const rates = ref([]); // 환율 데이터
    const historicalRates = ref([]); // 과거 환율 데이터
    const amount = ref(1); // 시작 금액 (KRW)
    const convertedAmount = ref(null); // 환전 금액
    const fromCurrency = ref({ code: "USD", name: "미국 달러", rate: null }); // 시작 통화
    const toCurrency = ref({ code: "KRW", name: "한국 원화", rate: 1 }); // 도착 통화
    const error = ref(null); // 에러 메시지
    const statistics = ref({}); // 통계 데이터
    const updateCounter = ref(0); // 업데이트 카운터
    const chartData = ref(null); // 차트 데이터
    const chartInstance = ref(null); // 차트 인스턴스
    const chartCanvas = ref(null); // 차트 캔버스
    const isChartCreating = ref(false); // 차트 생성 상태

    const commonCurrencies = ref([
        { code: 'KRW', name: '한국 원화', rate: 1 },
        { code: 'AED', name: 'UAE 디르함', rate: null },
        { code: 'AUD', name: '호주 달러', rate: null },
        { code: 'BHD', name: '바레인 디나르', rate: null },
        { code: 'BND', name: '브루나이 달러', rate: null },
        { code: 'CAD', name: '캐나다 달러', rate: null },
        { code: 'CHF', name: '스위스 프랑', rate: null },
        { code: 'CNH', name: '중국 위안화', rate: null },
        { code: 'DKK', name: '덴마크 크로네', rate: null },
        { code: 'EUR', name: '유럽연합 유로', rate: null },
        { code: 'GBP', name: '영국 파운드', rate: null },
        { code: 'HKD', name: '홍콩 달러', rate: null },
        { code: 'IDR(100)', name: '인도네시아 루피아', rate: null },
        { code: 'JPY(100)', name: '일본 엔', rate: null },
        { code: 'KWD', name: '쿠웨이트 디나르', rate: null },
        { code: 'MYR', name: '말레이시아 링깃', rate: null },
        { code: 'NOK', name: '노르웨이 크로네', rate: null },
        { code: 'NZD', name: '뉴질랜드 달러', rate: null },
        { code: 'SAR', name: '사우디 리얄', rate: null },
        { code: 'SEK', name: '스웨덴 크로나', rate: null },
        { code: 'SGD', name: '싱가포르 달러', rate: null },
        { code: 'THB', name: '태국 바트', rate: null },
        { code: 'USD', name: '미국 달러', rate: null },
      ]);

    const fetchRates = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/exchange/rates/");
        rates.value = response.data;

        // commonCurrencies 환율 업데이트
        commonCurrencies.value.forEach((currency) => {
          if (currency.code !== "KRW") {
            const foundRate = rates.value.find(
              (rate) => rate.cur_unit === currency.code
            );
            if (foundRate) {
              currency.rate = parseFloat(
                foundRate.deal_bas_r.replace(/,/g, "")
              );
            }
          }
        });

        // USD 환율 기본값 설정
        fromCurrency.value.rate = commonCurrencies.value.find(
          (currency) => currency.code === "USD"
        )?.rate;

        // 초기 환전 계산 수행
        calculateConversion();
      } catch (err) {
        console.error("Error fetching rates:", err);
        error.value = "환율 데이터를 가져오는 데 실패했습니다.";
      }
    };
    const fetchHistoricalRates = async () => {
      if (!fromCurrency.value || !toCurrency.value?.code) return;

      try {
        const response = await axios.get(
          `http://127.0.0.1:8000/api/exchange/rates/chart/`,
          {
            params: {
              from: fromCurrency.value.code,
              to: toCurrency.value.code,
              days: 7,
            },
          }
        );

        // 데이터가 있는지 확인
        if (!response.data?.data) {
          throw new Error('Invalid response data');
        }

        historicalRates.value = response.data.data.rates.map((rate, index) => ({
          date: response.data.data.dates[index],
          rate: rate,
        }));
        
        statistics.value = {
          mean: response.data.data.mean,
          std: response.data.data.std,
          min: response.data.data.min,
          max: response.data.data.max
        };

        // nextTick을 사용하여 DOM 업데이트 후 차트 생성
        nextTick(() => {
          createChart(
            response.data.data.dates,
            response.data.data.rates
          );
        });
      } catch (err) {
        console.error("Error fetching historical rates:", err);
        error.value = "과거 환율 데이터를 가져오는 데 실패했습니다.";
      }
    };

    watch([fromCurrency, toCurrency], fetchHistoricalRates);

    const getRate = (currency) => {
      if (!currency) return null;

      if (currency.code === "KRW") return 1;

      if (isCommonCurrency(currency)) {
        return currency.rate;
      }

      if (currency.deal_bas_r) {
        return parseFloat(currency.deal_bas_r.replace(/,/g, ""));
      }

      return null;
    };

    const calculateConversion = () => {
      if (!fromCurrency.value || !toCurrency.value || !amount.value) {
        convertedAmount.value = null;
        return;
      }

      const fromRate = getRate(fromCurrency.value);
      const toRate = getRate(toCurrency.value);

      if (fromRate === null || toRate === null) {
        convertedAmount.value = null;
        error.value = "유효하지 않은 환율입니다.";
        return;
      }

      try {
        const amountInKRW = amount.value * fromRate;
        convertedAmount.value =  Number((amountInKRW / toRate).toFixed(2));
        error.value = null;
      } catch (err) {
        console.error("Calculation error:", err);
        error.value = "환율 계산 중 오류가 발생했습니다.";
      }
    };
    const calculateReverseConversion = () => {
      if (!fromCurrency.value || !toCurrency.value || convertedAmount.value === null) {
        amount.value = null;
        return;
      }

      const fromRate = getRate(fromCurrency.value);
      const toRate = getRate(toCurrency.value);

      if (fromRate === null || toRate === null) {
        amount.value = null;
        error.value = "유효하지 않은 환율입니다.";
        return;
      }

      try {
        const amountInKRW = convertedAmount.value * toRate;
        amount.value = Number((amountInKRW / fromRate).toFixed(2));
        error.value = null;
      } catch (err) {
        console.error("Reverse calculation error:", err);
        error.value = "역방향 환율 계산 중 오류가 발생했습니다.";
      }
    };

    const isCommonCurrency = (currency) =>
      currency && typeof currency.code !== "undefined";

    const formatAmount = (value) =>
      new Intl.NumberFormat("ko-KR", {
        maximumFractionDigits: 2,
        minimumFractionDigits: 2,
      }).format(value);

    const getFromCurrencyCode = () =>
      fromCurrency.value
        ? fromCurrency.value.code || fromCurrency.value.CUR_UNIT
        : "";

    const getToCurrencyCode = () =>
      toCurrency.value
        ? toCurrency.value.code || toCurrency.value.CUR_UNIT
        : "";

    // 시작 통화와 도착 통화를 스위치
    const switchCurrencies = () => {
      const temp = fromCurrency.value;
      fromCurrency.value = toCurrency.value;
      toCurrency.value = temp;

      const tempAmount = amount.value;
      amount.value = convertedAmount.value;
      convertedAmount.value = tempAmount;
    };

    // 디바운스 함수 추가
    const debounce = (fn, delay) => {
      let timeoutId;
      return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
      };
    };

    // 도착 통화 변경 시 환율 계산
    watch([toCurrency], () => {
      if (updateCounter.value < 1) {
        updateCounter.value++;
        calculateReverseConversion();
      } else {
        updateCounter.value = 0;
      }
    });

    // 시작 통화 변경 시 환율 계산
    watch([fromCurrency], () => {
      if (updateCounter.value < 1) {
        updateCounter.value++;
        calculateConversion();
      } else {
        updateCounter.value = 0;
      }
    });

    // amount watch 수정
    watch([amount], () => {
      if (updateCounter.value < 1) {
        updateCounter.value++;
        calculateConversion();
      } else {
        updateCounter.value = 0;
      }
    });

    // convertedAmount watch 수정
    watch([convertedAmount], () => {
      if (updateCounter.value < 1) {
        updateCounter.value++;
        calculateReverseConversion();
      } else {
        updateCounter.value = 0;
      }
    });

    // 컴포넌트가 로드될 때 실행
    onMounted(() => {
      fetchRates();
      fetchHistoricalRates();
    });

    // 국가 코드와 국기 URL을 가져오는 함수
    const getCountryFlag = (currencyCode) => {
      const countryCode = getCountryCodeByCurrency(currencyCode);
      return getFlagByCountryCode(countryCode);
    };

    const createChart = async (dates, rates) => {
      if (isChartCreating.value) return;
      isChartCreating.value = true;

      try {
        if (chartInstance.value) {
          chartInstance.value.destroy();
          chartInstance.value = null;
        }

        await nextTick();

        const ctx = chartCanvas.value?.getContext('2d');
        if (!ctx) return;

        chartInstance.value = new Chart(ctx, {
          type: 'line',
          data: {
            labels: dates,
            datasets: [{
              data: rates,
              borderColor: '#007bff',
              borderWidth: 2,
              pointStyle: 'circle',
              pointRadius: 6,
              pointHoverRadius: 8,
              pointBackgroundColor: 'white',
              pointBorderColor: '#007bff',
              pointBorderWidth: 2,
              tension: 0.1,
              fill: false,
            }]
          },
          options: {
            animation: {
              duration: 0  // 오기 로딩만 즉시
            },
            maintainAspectRatio: false,
            responsive: true,
            interaction: {
              intersect: false,
              mode: 'index'
            },
            plugins: {
              tooltip: {
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                titleColor: '#666',
                bodyColor: '#666',
                borderColor: '#ddd',
                borderWidth: 1,
                padding: 10,
                displayColors: false,
                position: 'nearest',
                titleFont: {
                  size: 17
                },
                bodyFont: {
                  size: 23
                },
                callbacks: {
                  title: function(context) {
                    return context[0].label;
                  },
                  label: function(context) {
                    return `환율: ${new Intl.NumberFormat('ko-KR', {
                      maximumFractionDigits: 2,
                      minimumFractionDigits: 2
                    }).format(context.parsed.y)}`;
                  }
                }
              },
              crosshair: {
                line: {
                  color: '#666',
                  width: 1,
                  dashPattern: [5, 5]
                },
                sync: {
                  enabled: true,
                  group: 1
                },
                zoom: {
                  enabled: false
                },
                snap: {
                  enabled: true
                },
                callbacks: {
                  beforeDraw: (chart) => {
                    const activeElements = chart.getActiveElements();
                    if (activeElements.length > 0) {
                      const activePoint = activeElements[0];
                      const ctx = chart.ctx;
                      const yAxis = chart.scales.y;
                      const xAxis = chart.scales.x;
                      const x = activePoint.element.x;
                      const y = activePoint.element.y;

                      // 세로선
                      ctx.save();
                      ctx.beginPath();
                      ctx.setLineDash([5, 5]);
                      ctx.moveTo(x, yAxis.top);
                      ctx.lineTo(x, yAxis.bottom);
                      ctx.lineWidth = 1;
                      ctx.strokeStyle = 'rgba(102, 102, 102, 0.5)';
                      ctx.stroke();

                      // 가로선
                      ctx.beginPath();
                      ctx.moveTo(xAxis.left, y);
                      ctx.lineTo(xAxis.right, y);
                      ctx.stroke();
                      ctx.restore();
                    }
                  }
                }
              },
              legend: {
                display: false
              }
            },
            scales: {
              x: {
                grid: {
                  display: false
                },
                ticks: {
                  font: {
                    size: 11
                  }
                }
              },
              y: {
                grid: {
                  display: false
                },
                ticks: {
                  font: {
                    size: 11
                  }
                }
              }
            }
          }
        });
      } catch (error) {
        console.error('Error creating chart:', error);
      } finally {
        isChartCreating.value = false;
      }
    };

    // formatNumber 함수 추가
    const formatNumber = (value) => {
      if (value === null || value === undefined) return '';
      return new Intl.NumberFormat('ko-KR').format(value);
    };

    return {
      rates,
      historicalRates,
      amount,
      fromCurrency,
      toCurrency,
      convertedAmount,
      error,
      chartData,
      statistics,
      fetchRates,
      fetchHistoricalRates,
      commonCurrencies,
      formatAmount,
      getFromCurrencyCode,
      getToCurrencyCode,
      switchCurrencies,
      getCountryFlag,
      chartCanvas,
      formatNumber,
    };
  },
};
</script>

<style scoped>
.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background: #f8f9fa;
}

.calculator-wrapper {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 2rem;
}

.calculator-container {
  display: grid;
  grid-template-columns: 5fr 1fr 5fr;
  gap: 2rem;
  align-items: center;
  padding: 1rem;
}

.currency-section {
  padding: 1.5rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.currency-select {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.currency-flag {
  width: 50px;
  height: 30px;
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  border-radius: 10%;
  object-fit: cover;
  border: 2px solid #e0e0e0;
}

.currency-select select,
.amount-input input {
  width: 340px;
  height: 48px;
  padding: 12px 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: white;
  font-size: 1rem;
}

.currency-select select {
  padding-left: 70px;
  appearance: none;
  cursor: pointer;
  width: 370px;
}

.amount-input input {
  text-align: left;
  background-color: rgb(214, 214, 214);
}

.switch-button {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #007bff;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.5rem;
  color: white;
}

.switch-button:hover {
  background-color: #0056b3;
  transform: scale(1.1);
}

.statistics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin: 2rem 0;
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.2rem;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  transition: transform 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.stat-value {
  font-size: 1.4rem;
  font-weight: 600;
  color: #333;
}

.min .stat-value {
  color: #dc3545;
}

.mean .stat-value {
  color: #198754;
}

.max .stat-value {
  color: #0d6efd;
}

@media (max-width: 768px) {
  .statistics {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .stat-item {
    padding: 1rem;
  }
  
  .stat-value {
    font-size: 1.2rem;
  }
}

.banner {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  color: #333;
  text-decoration: none;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: block;
  height: 100%;
}

.banner:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
}

.banner-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  height: 100%;
}

.banner-content i {
  font-size: 2rem;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.banner-content h3 {
  margin: 0.5rem 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.banner-content p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.8;
}

select:focus,
input:focus {
  outline: none;
  border-color: #ffffff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

select:hover,
input:hover {
  border-color: #007bff;
}

.exchange-calculator-title {
  font-size: 2rem;
  color: #333;
  margin-bottom: 2rem;
  text-align: center;
}

.error {
  color: #dc3545;
  text-align: center;
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: #f8d7da;
  border-radius: 8px;
}

@media (max-width: 1200px) {
  .main-container {
    grid-template-columns: 1fr;
    max-width: 900px;
  }
}

.right-section {
  display: flex;
  flex-direction: column;
  gap: 3.5rem;
  padding: 1rem 0;
}

.switch-section {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.chart-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chart-container {
  position: relative;
  height: 400px;
  width: 100%;
}

.statistics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-top: auto;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.2rem;
  font-weight: 600;
}

.min .stat-value { color: #dc3545; }
.mean .stat-value { color: #198754; }
.max .stat-value { color: #0d6efd; }

@media (max-width: 768px) {
  .statistics {
    grid-template-columns: 1fr;
  }
}

</style>
