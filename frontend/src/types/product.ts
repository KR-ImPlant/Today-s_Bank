export interface Product {
  id?: number;
  fin_prdt_cd: string;          // 금융상품코드
  kor_co_nm: string;            // 금융회사명
  fin_prdt_nm: string;          // 금융상품명
  join_way: string;             // 가입방법
  join_deny: number;            // 가입제한
  join_member: string;          // 가입대상
  etc_note: string;             // 기타유의사항
  max_limit: number;            // 최고한도
  dcls_strt_day: string;        // 공시시작일
  dcls_end_day: string;         // 공시종료일
  fin_co_subm_day: string;      // 금융회사 제출일
  intr_rate_type: string;       // 금리유형
  intr_rate_type_nm: string;    // 금리유형명
  intr_rate: number;            // 기본금리
  intr_rate2: number;           // 최고금리
  save_trm: string;             // 저축기간
  spcl_cnd: string;            // 우대조건
}

export interface BankInfo {
  name: string;
  logo: string;
}