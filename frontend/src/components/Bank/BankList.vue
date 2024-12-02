<script>
import { ref, onMounted, onBeforeUnmount } from 'vue';

export default {
  setup() {
    const map = ref(null);                    // 카카오맵 인스턴스
    const markers = ref([]);                  // 지도 위 마커들
    const displayedList = ref([]);            // 화면에 표시될 은행 목록
    const ps = ref(null);                     // 장소 검색 서비스
    const infowindow = ref(null);             // 마커 클릭시 표시될 정보창
    const currentLocation = ref(null);        // 사용자 현재 위치
    const defaultPosition = { lat: 36.1072135, lng: 128.4034859 }; // 기본 지도 중심 위치
    const highlightedBank = ref(null);        // 현재 선택된 은행
    const searchQuery = ref('');              // 검색어
    const bankFilter = ref('');               // 은행 필터 (특정 은행만 보기)
    const sortBy = ref('distance');           // 정렬 기준
    
    // 은행 목록 항목 클릭 처리
    const handleBranchClick = (bank, index) => {
      // 선택된 은행 하이라이트
      highlightedBank.value = index;
      
      // 해당 은행 위치로 지도 중심 이동
      const position = new window.kakao.maps.LatLng(bank.y, bank.x);
      map.value.setCenter(position);
      
      // 목록에서 해당 은행으로 스크롤
      const listElement = document.querySelector(`.branch-detail li:nth-child(${index + 1})`);
      if (listElement) {
        listElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      
      // 해당 마커의 클릭 이벤트 트리거
      const marker = markers.value[index];
      window.kakao.maps.event.trigger(marker, 'click');
    };
    // 카카오맵 초기화 및 로드
    const loadKakaoMap = () => {
      // 카카오맵 SDK가 없으면 로드
      if (!window.kakao || !window.kakao.maps) {
        const script = document.createElement('script');
        script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_MAP_KEY}&libraries=services&autoload=false`;
        script.addEventListener('load', () => {
          window.kakao.maps.load(initMap);
        });
        document.head.appendChild(script);
      } else {
        window.kakao.maps.load(initMap);
      }
    };

    const initMap = () => {
      const mapContainer = document.getElementById('map');
      const mapOption = {
        center: new window.kakao.maps.LatLng(defaultPosition.lat, defaultPosition.lng),
        level: 3,
      };

      map.value = new window.kakao.maps.Map(mapContainer, mapOption);
      ps.value = new window.kakao.maps.services.Places();
      infowindow.value = new window.kakao.maps.InfoWindow({
        zIndex: 1,
        removable: true, // 닫기 버튼 기본 제공
      });


      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(handleGeolocationSuccess, handleGeolocationError);
      } else {
        searchNearbyBranches(defaultPosition.lat, defaultPosition.lng);
      }

      window.kakao.maps.event.addListener(map.value, 'dragend', handleMapDragEnd);
    };

    const handleGeolocationSuccess = (position) => {
      const lat = position.coords.latitude;
      const lng = position.coords.longitude;
      currentLocation.value = { lat, lng };
      map.value.setCenter(new window.kakao.maps.LatLng(lat, lng));
      searchNearbyBranches(lat, lng);
    };

    const handleGeolocationError = () => {
      alert('현재 위치를 가져올 수 없어 기본 위치로 설정합니다.');
      searchNearbyBranches(defaultPosition.lat, defaultPosition.lng);
    };

    // 주변 은행 검색
    const searchNearbyBranches = (lat, lng) => {
      clearMarkersAndList();
      highlightedBank.value = null;

      const radius = calculateSearchRadius();
      const searchOptions = {
        location: new window.kakao.maps.LatLng(lat, lng),
        radius: radius,
      };

      // 은행 필터가 있는 경우, 해당 은행만 키워드 검색
      if (bankFilter.value) {
        ps.value.keywordSearch(bankFilter.value, (data, status) => {
          if (status === window.kakao.maps.services.Status.OK) {
            // 은행 카테고리(BK9)에 해당하는 결과만 필터링
            const bankResults = data.filter(place => 
              place.category_group_code === 'BK9' &&
              place.place_name.includes(bankFilter.value)
            );
            updateMarkersAndList(bankResults);
          }
        }, searchOptions);
      } else {
        // 필터가 없는 경우 모든 은행 검색
        ps.value.categorySearch('BK9', placesSearchCB, searchOptions);
      }
    };

    const placesSearchCB = (data, status) => {
      if (status === window.kakao.maps.services.Status.OK) {
        updateMarkersAndList(data);
      }
    };

    const updateMarkersAndList = async (places) => {
      // 기존 마커와 목록 초기화
      clearMarkersAndList();
      
      // 모든 장소에 대해 로드뷰 가능 여부 체크
      const placesWithRoadview = await Promise.all(
        places.map(async (place) => ({
          ...place,
          hasRoadview: await checkRoadviewAvailable(place.y, place.x),
          distance: currentLocation.value ? 
            calculateDistance(
              currentLocation.value.lat,
              currentLocation.value.lng,
              place.y,
              place.x
            ) : 0
        }))
      );

      // 정렬 적용
      let sortedPlaces = [...placesWithRoadview];
      if (sortBy.value === 'distance' && currentLocation.value) {
        sortedPlaces.sort((a, b) => a.distance - b.distance);
      } else if (sortBy.value === 'name') {
        sortedPlaces.sort((a, b) => a.place_name.localeCompare(b.place_name));
      }

      // 정렬된 결과를 마커와 목록에 추가
      sortedPlaces.forEach((place, index) => {
        addPlaceMarker(place, index);
        displayedList.value.push(place);
      });
    };

    const addPlaceMarker = (place, index) => {
      const position = new window.kakao.maps.LatLng(place.y, place.x);
      
      // 숫자 마커 이미지 설정
      const imageSrc = 'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/marker_number_blue.png';
      const imageSize = new window.kakao.maps.Size(36, 37);
      const imgOptions = {
        spriteSize: new window.kakao.maps.Size(36, 691),
        spriteOrigin: new window.kakao.maps.Point(0, (index * 46) + 10),
        offset: new window.kakao.maps.Point(13, 37),
      };

      const markerImage = new window.kakao.maps.MarkerImage(imageSrc, imageSize, imgOptions);
      
      const marker = new window.kakao.maps.Marker({
        position: position,
        map: map.value,
        image: markerImage,
      });

      window.kakao.maps.event.addListener(marker, 'click', () => {
        highlightedBank.value = index;

        // 해당 은행 목록 요소로 스크롤
        const listElement = document.querySelector(`.branch-detail li:nth-child(${index + 1})`);
        if (listElement) {
          listElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        navigator.geolocation.getCurrentPosition((position) => {
          const startLat = position.coords.latitude;
          const startLng = position.coords.longitude;
          const distance = calculateDistance(startLat, startLng, place.y, place.x);
          const walkingTime = Math.round(distance / 67);
          const drivingTime = Math.round(distance / 500);

          const content = `
            <div style="padding: 15px; width: 250px; font-family: 'Noto Sans KR', sans-serif;">
              <div style="margin-bottom: 12px;">
                <strong style="font-size: 16px; color: #37474F;">
                  ${index + 1}. ${place.place_name}
                </strong>
              </div>
              
              <div style="margin-bottom: 12px; font-size: 13px; color: #666;">
                <p>🚶 도보: 약 ${walkingTime}분</p>
                <p>🚗 차량: 약 ${drivingTime}분</p>
              </div>
              
              <div style="display: flex; gap: 8px;">
                <a href="https://map.kakao.com/link/to/${place.place_name},${place.y},${place.x}" 
                   target="_blank" 
                   style="
                     flex: 1;
                     padding: 8px 0;
                     background: #4CAF50;
                     color: white;
                     text-decoration: none;
                     border-radius: 4px;
                     font-size: 13px;
                     text-align: center;
                   ">
                  길찾기
                </a>
                ${place.hasRoadview ? `
                  <button 
                    onclick="document.dispatchEvent(new CustomEvent('openRoadview', {detail: {lat: ${place.y}, lng: ${place.x}}}))"
                    style="
                      flex: 1;
                      padding: 8px 0;
                      background: #2196F3;
                      color: white;
                      border: none;
                      border-radius: 4px;
                      cursor: pointer;
                      font-size: 13px;
                    ">
                    로드뷰
                  </button>
                ` : ''}
              </div>
            </div>
          `;
          
          infowindow.value.setContent(content);
          infowindow.value.open(map.value, marker);
        });
      });

      // 마우스 오버 인포윈도우도 개선
      const mouseOverInfo = new window.kakao.maps.InfoWindow({
        content: `
          <div style="
            padding: 8px 12px;
            font-family: 'Noto Sans KR', sans-serif;
            font-size: 13px;
            color: #37474F;
            background: white;
            border-radius: 4px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
          ">
            ${index + 1}. ${place.place_name}
          </div>
        `,
      });

      window.kakao.maps.event.addListener(marker, 'mouseover', () => {
        mouseOverInfo.open(map.value, marker);
      });
      window.kakao.maps.event.addListener(marker, 'mouseout', () => {
        mouseOverInfo.close();
      });

      markers.value.push(marker);
    };



    const clearMarkersAndList = () => {
      markers.value.forEach((marker) => marker.setMap(null));
      markers.value = [];
      displayedList.value = [];
    };

    const handleMapDragEnd = () => {
      const center = map.value.getCenter();
      searchNearbyBranches(center.getLat(), center.getLng());
    };

    const calculateSearchRadius = () => {
      const bounds = map.value.getBounds();
      const center = map.value.getCenter();
      const sw = bounds.getSouthWest();
      const line = new window.kakao.maps.Polyline({ path: [center, sw] });
      return Math.min(line.getLength(), 2000);
    };

    let isRoadViewOpen = false; // 로드뷰 상태 관리 변수

    // 로드뷰 관련 기능
    const loadRoadView = (lat, lng) => {
      // 백그라운드 오버레이 생성
      const overlay = document.createElement('div');
      overlay.id = 'roadview-overlay';
      overlay.style.position = 'fixed';
      overlay.style.top = '0';
      overlay.style.left = '0';
      overlay.style.width = '100vw';
      overlay.style.height = '100vh';
      overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
      overlay.style.zIndex = '9998'; // 로드뷰 아래에 표시
      overlay.addEventListener('click', () => {
        document.body.removeChild(overlay);
        document.body.removeChild(roadviewContainer);
      });

      // 로드뷰 컨테이너 생성
      const roadviewContainer = document.createElement('div');
      roadviewContainer.id = 'roadview-container';
      roadviewContainer.style.position = 'fixed';
      roadviewContainer.style.top = '50%';
      roadviewContainer.style.left = '50%';
      roadviewContainer.style.transform = 'translate(-50%, -50%)';
      roadviewContainer.style.width = '800px';
      roadviewContainer.style.height = '600px';
      roadviewContainer.style.backgroundColor = '#fff';
      roadviewContainer.style.zIndex = '9999';
      roadviewContainer.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
      roadviewContainer.style.borderRadius = '8px';

      // 닫기 버튼 추가
      const closeButton = document.createElement('button');
      closeButton.innerText = '닫기';
      closeButton.style.position = 'absolute';
      closeButton.style.top = '10px';
      closeButton.style.right = '10px';
      closeButton.style.zIndex = '10000';
      closeButton.style.padding = '5px 10px';
      closeButton.style.cursor = 'pointer';
      closeButton.style.backgroundColor = '#007bff';
      closeButton.style.color = 'white';
      closeButton.style.border = 'none';
      closeButton.style.borderRadius = '5px';
      closeButton.addEventListener('click', () => {
        document.body.removeChild(overlay);
        document.body.removeChild(roadviewContainer);
      });

      roadviewContainer.appendChild(closeButton);
      document.body.appendChild(overlay);
      document.body.appendChild(roadviewContainer);

  const roadview = new window.kakao.maps.Roadview(roadviewContainer);
  const roadviewClient = new window.kakao.maps.RoadviewClient();

  try {
    const position = new window.kakao.maps.LatLng(lat, lng);
    roadviewClient.getNearestPanoId(position, 50, (panoId) => {
      if (panoId) {
        roadview.setPanoId(panoId, position);
      } else {
        alert('로드뷰를 찾을 수 없습니다.');
        document.body.removeChild(overlay);
        document.body.removeChild(roadviewContainer);
      }
    });
  } catch (error) {
    alert('로드뷰를 생성할 수 없습니다.');
        document.body.removeChild(overlay);
        document.body.removeChild(roadviewContainer);
      }
    };

    const checkRoadviewAvailable = async (lat, lng) => {
      const position = new window.kakao.maps.LatLng(lat, lng);
      const roadviewClient = new window.kakao.maps.RoadviewClient();
      
      return new Promise((resolve) => {
        roadviewClient.getNearestPanoId(position, 50, (panoId) => {
          resolve(!!panoId);
        });
      });
    };

    const handleSearch = () => {
      if (!searchQuery.value.trim()) return;  // 빈 검색어 처리

      // 1. 키워드 검색
      ps.value.keywordSearch(searchQuery.value, (data, status) => {
        if (status === window.kakao.maps.services.Status.OK) {
          // 검색 결과 중 은행만 필터링
          const bankResults = data.filter(place => 
            place.category_group_code === 'BK9' || 
            place.category_name.includes('은행')
          );
          
          if (bankResults.length > 0) {
            // 검색된 첫 번째 결과로 지도 중심 이동
            const firstResult = bankResults[0];
            const moveLatLon = new window.kakao.maps.LatLng(
              firstResult.y, 
              firstResult.x
            );
            
            map.value.setCenter(moveLatLon);
            map.value.setLevel(3);  // 줌 레벨 설정
            
            // 주변 은행 검색 트리거
            searchNearbyBranches(firstResult.y, firstResult.x);
          } else {
            // 은행 검색 결과가 없으면 일반 장소로 검색
            const moveLatLon = new window.kakao.maps.LatLng(
              data[0].y, 
              data[0].x
            );
            
            map.value.setCenter(moveLatLon);
            map.value.setLevel(3);
            searchNearbyBranches(data[0].y, data[0].x);
          }
        }
      });
    };

    const moveToCurrentLocation = () => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            const moveLatLon = new window.kakao.maps.LatLng(lat, lng);
            map.value.setCenter(moveLatLon);
            map.value.setLevel(3);  // 줌 레벨 설정
            
            // 주변 은행 검색
            searchNearbyBranches(lat, lng);
          },
          () => {
            // 위치 정보 획득 실패 시 조용히 실패 처리
          }
        );
      }
    };

    // 필터와 정렬 적용
    const applyFilters = () => {
      const center = map.value.getCenter();
      searchNearbyBranches(center.getLat(), center.getLng());
    };
    
    const setSortBy = (type) => {
      sortBy.value = type;
      applyFilters();
    };

    // 거리 계산 함수 (하버사인 공식)
    const calculateDistance = (lat1, lon1, lat2, lon2) => {
      const R = 6371e3; // 지구의 반지름 (미터)
      const φ1 = lat1 * Math.PI/180;
      const φ2 = lat2 * Math.PI/180;
      const Δφ = (lat2-lat1) * Math.PI/180;
      const Δλ = (lon2-lon1) * Math.PI/180;

      const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ/2) * Math.sin(Δλ/2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

      return R * c; // 미터 단위
    };

    onMounted(loadKakaoMap);

    // 이벤트 핸들러 함수를 별도로 정의
    const handleRoadviewOpen = (e) => {
      loadRoadView(e.detail.lat, e.detail.lng);
    };

    onMounted(() => {
      document.addEventListener('openRoadview', handleRoadviewOpen);
    });

    onBeforeUnmount(() => {
      document.removeEventListener('openRoadview', handleRoadviewOpen);
    }); 

    return {
      displayedList,
      highlightedBank,
      handleBranchClick,
      checkRoadviewAvailable,
      loadRoadView,
      searchQuery,
      handleSearch,
      moveToCurrentLocation,
      bankFilter,
      sortBy,
      applyFilters,
      setSortBy,
    };
  },
};
</script>

<template>
  <div class="map-container">
    <div class="branch-detail">
      <div class="branch-header">
        <div class="search-container">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="은행명 또는 지역을 검색하요"
            @keyup.enter="handleSearch"
          />
          <button @click="handleSearch">
            <i class="fas fa-search"></i>
          </button>
        </div>
        
        <!-- 필터 옵션 -->
        <div class="filter-container">
          <select v-model="bankFilter" @change="applyFilters">
            <option value="">모든 은행</option>
            <option value="신한은행">신한은행</option>
            <option value="국민은행">국민은행</option>
            <option value="우리은행">우리은행</option>
            <option value="하나은행">하나은행</option>
            <option value="농협은행">농협은행</option>
            <option value="기업은행">기업은행</option>
          </select>

          <div class="sort-options">
            <button 
              :class="{ active: sortBy === 'distance' }"
              @click="setSortBy('distance')"
            >
              거리순
            </button>
            <button 
              :class="{ active: sortBy === 'name' }"
              @click="setSortBy('name')"
            >
              이름순
            </button>
          </div>
        </div>
      </div>
      <ul>
        <li
          v-for="(bank, index) in displayedList"
          :key="index"
          :class="{ selected: highlightedBank === index }"
          @click="handleBranchClick(bank, index)"
        >
          <div class="bank-item">
            <div class="bank-number">{{ index + 1 }}</div>
            <div class="bank-info">
              <strong>{{ bank.place_name }}</strong>
              <p><i class="fas fa-location-dot"></i> {{ bank.address_name }}</p>
              <p style="position: relative;">
                <i class="fas fa-phone"></i> {{ bank.phone || '정보 없음' }}
                <template v-if="bank.hasRoadview">
                  <i class="fas fa-camera" 
                     style="cursor: pointer; position: absolute; right: 0;" 
                     @click.stop="loadRoadView(bank.y, bank.x)"
                     title="로드뷰 보기"></i>
                </template>
              </p>
            </div>
          </div>
        </li>
      </ul>
    </div>
    <div id="map" class="map"></div>
    <button 
      class="my-location-btn"
      @click="moveToCurrentLocation"
      title="내 위치로 이동"
    >
      <i class="fas fa-compass"></i>
    </button>
  </div>
</template>

<style lang="scss" scoped>
.map-container {
  display: flex;
  justify-content: center;
  height: calc(100vh - 180px);
  padding: 20px;
  gap: 20px;

  .branch-detail {
    width: 380px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    overflow-y: hidden;
    height: 100%;
    display: flex;
    flex-direction: column;

    .branch-header {
      background: #37474f;
      color: white;
      padding: 1rem;
      border-radius: 12px 12px 0 0;
      
      .search-container {
        display: flex;
        gap: 8px;
        width: 100%;
        
        input {
          flex: 1;
          padding: 8px 12px;
          border: none;
          border-radius: 6px;
          font-size: 14px;
          background: white;
          
          &:focus {
            outline: none;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
          }

          &::placeholder {
            color: #9E9E9E;
          }
        }
        
        button {
          padding: 0 12px;
          border: none;
          border-radius: 6px;
          background: #2196F3;
          color: white;
          cursor: pointer;
          transition: background-color 0.2s ease;
          
          &:hover {
            background: #1976D2;
          }

          &:active {
            background: #1565C0;
          }
        }
      }
    }

    ul {
      list-style: none;
      padding: 1rem;
      margin: 0;
      overflow-y: auto;
      flex: 1;
    }

    li {
      margin-bottom: 0.8rem;
      border-radius: 8px;
      transition: all 0.3s ease;
      cursor: pointer;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      }

      &.selected {
        background-color: #f5f5f5;
        border-left: 4px solid #546e7a;
      }

      .bank-item {
        display: flex;
        gap: 1rem;
        padding: 1rem;

        .bank-number {
          background: #546e7a;
          color: white;
          width: 28px;
          height: 28px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          flex-shrink: 0;
        }

        .bank-info {
          flex: 1;

          strong {
            display: block;
            color: #37474f;
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
          }

          p {
            margin: 0.3rem 0;
            color: #78909c;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;

            i {
              color: #546e7a;
              width: 16px;
            }

            i.fa-camera {
              color: #2196F3;
              float: right;
              margin-left: 1rem;
              
              &:hover {
                color: #1976D2;
                transform: scale(1.1);
                transition: all 0.2s ease;
              }
            }
          }
        }
      }
    }
  }

  .map {
    flex: 1;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  .my-location-btn {
    position: absolute;
    bottom: 30px;
    right: 30px;
    width: 45px;
    height: 45px;
    border-radius: 50%;
    background: white;
    border: none;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    cursor: pointer;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    
    i {
      color: #2196F3;
      font-size: 22px;
      transition: transform 0.3s ease;
    }

    &:hover {
      background: #f5f5f5;
      box-shadow: 0 4px 8px rgba(0,0,0,0.2);
      transform: translateY(-2px);
      
      i {
        transform: rotate(30deg);
      }
    }

    &:active {
      transform: translateY(0);
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      
      i {
        transform: rotate(60deg);
      }
    }
  }
}

@media screen and (max-width: 768px) {
  .map-container {
    flex-direction: column;
    height: calc(100vh - 180px);

    .branch-detail {
      width: 100%;
      height: auto;
      max-height: 300px;
    }

    .map {
      height: 100%;
      width: 100%;
    }

    .my-location-btn {
      bottom: 20px;
      right: 20px;
    }
  }
}

#roadview-container {
  border-radius: 12px;
  overflow: hidden;
}

#roadview-overlay {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.filter-container {
  margin-top: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  
  select {
    flex: 1;
    padding: 8px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background: white;
    font-size: 14px;
    
    &:focus {
      outline: none;
      border-color: #2196F3;
    }
  }
  
  .sort-options {
    display: flex;
    gap: 8px;
    
    button {
      padding: 6px 12px;
      border: 1px solid #e0e0e0;
      border-radius: 4px;
      background: white;
      font-size: 13px;
      cursor: pointer;
      transition: all 0.2s ease;
      
      &.active {
        background: #2196F3;
        color: white;
        border-color: #2196F3;
      }
      
      &:hover:not(.active) {
        background: #f5f5f5;
      }
    }
  }
}
</style>

