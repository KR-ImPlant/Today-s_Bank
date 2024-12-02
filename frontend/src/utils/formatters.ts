export const formatDate = (dateString: string) => {
  if (!dateString) return '정보없음';
  
  const year = dateString.slice(0, 4);
  const month = dateString.slice(4, 6);
  const day = dateString.slice(6, 8);
  
  return `${year}년 ${month}월 ${day}일`;
}; 