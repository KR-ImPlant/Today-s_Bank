<template>
  <div class="article-container">
    <div class="community-header">
      <div class="community-title">
        <h1>커뮤니티</h1>
        <p>오늘의 은행 회원들과 자유롭게 소통하세요</p>
      </div>
      <div class="header-actions">
        <button @click="showGuideModal" class="guide-button">
            <i class="fas fa-info-circle"></i> 이용안내
          </button>
        <button @click="showCreateModal" v-if="isAuthenticated" class="create-button">
          <i class="fas fa-pen"></i> 글쓰기
        </button>
      </div>
    </div>

    

    <div class="article-list">
      <div class="article-header">
      </div>

      <table>
        <thead>
          <tr>
            <th>번호</th>
            <th>제목</th>
            <th>작성자</th>
            <th>작성일</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="article in articles" :key="article.id" @click="showDetailModal(article.id)">
            <td>{{ article.id }}</td>
            <td>{{ article.title }}</td>
            <td>{{ article.nickname }}</td>
            <td>{{ formatDate(article.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isCreateModalOpen" class="modal" @click="closeModal">
      <div class="modal-content create-modal" @click.stop>
        <div class="modal-header">
          <h2>새 게시글 작성</h2>
        </div>
        <form @submit.prevent="createArticle" class="article-form">
          <div class="form-group">
            <!-- <label for="category">카테고리</label> -->
            <!-- <select 
              id="category"
              v-model="newArticle.category" 
              required
              class="category-select"
            >
              <option value="">카테고리 선택</option>
              <option value="free">자유게시판</option>
              <option value="info">금융정보</option>
              <option value="review">상품후기</option>
              <option value="qna">질문답변</option>
            </select> -->
          </div>
          <div class="form-group">
            <label for="title">제목</label>
            <input 
              id="title"
              v-model="newArticle.title" 
              type="text" 
              placeholder="제목을 입력하세요" 
              required
            >
          </div>
          <div class="form-group">
            <label for="content">내용</label>
            <textarea 
              id="content"
              v-model="newArticle.content" 
              placeholder="내용을 입력하세요" 
              required
            ></textarea>
          </div>
          <div class="form-group">

          </div>
          <div class="form-buttons">
            <button type="button" class="cancel-button" @click="closeModal">취소</button>
            <button type="submit" class="submit-button">등록</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="isDetailModalOpen" class="modal" @click="closeModal">
      <div class="modal-content detail-modal" @click.stop>
        <div v-if="selectedArticle" class="article-detail">
          <div class="modal-header">
            <h2>{{ selectedArticle.title }}</h2>
          </div>

          <div class="article-body">
            <div class="article-meta">
              <div class="author-info">
                <i class="fas fa-user"></i>
                <span>{{ selectedArticle.nickname }}</span>
              </div>
              <div class="date-info">
                <i class="fas fa-clock"></i>
                <span>{{ formatDate(selectedArticle.created_at) }}</span>
              </div>
              <div v-if="isArticleAuthor" class="article-actions">
                <button class="edit-button" @click="showEditArticleForm">
                  <i class="fas fa-edit"></i> 수정
                </button>
                <button class="delete-button" @click="deleteArticle">
                  <i class="fas fa-trash"></i> 삭제
                </button>
              </div>
            </div>

            <div v-if="isEditing" class="edit-form">
              <div class="form-group">
                <label for="edit-title">제목</label>
                <input 
                  id="edit-title"
                  v-model="editArticle.title" 
                  type="text" 
                  placeholder="제목을 입력하세요"
                >
              </div>
              <div class="form-group">
                <label for="edit-content">내용</label>
                <textarea 
                  id="edit-content"
                  v-model="editArticle.content" 
                  placeholder="내용을 입력하세요"
                ></textarea>
              </div>
              <div class="form-buttons">
                <button class="cancel-button" @click="cancelEdit">취소</button>
                <button class="submit-button" @click="updateArticle">저장</button>
              </div>
            </div>
            
            <div v-else class="article-content">
              <div v-if="selectedArticle.image" class="article-image">
                <img :src="`http://localhost:8000${selectedArticle.image}`" alt="게시글 이미지">

                <p>{{ selectedArticle.content }}</p>

              </div>
              <p>{{ selectedArticle.content }}</p>
            </div>

            <div class="comments-section">
              <h3>댓글 <span class="comment-count">{{ selectedArticle.comments?.length || 0 }}</span></h3>
              
              <div class="comment-form">
                <textarea 
                  v-model="newComment" 
                  placeholder="댓글을 작성하세요"
                  rows="3"
                ></textarea>
                <button @click="createComment" class="comment-submit">
                  <i class="fas fa-paper-plane"></i> 댓글 작성
                </button>
              </div>

              <div class="comments-list">
                <div v-for="comment in selectedArticle.comments" :key="comment.id" class="comment">
                  <div class="comment-header">
                    <div class="comment-author">
                      <i class="fas fa-user-circle"></i>
                      <span>{{ comment.nickname }}</span>
                    </div>
                    <div class="comment-date">
                      {{ formatDate(comment.created_at) }}
                    </div>
                  </div>
                  <div class="comment-content">
                    <p>{{ comment.content }}</p>
                  </div>
                  <div v-if="isCommentAuthor(comment)" class="comment-actions">
                    <button class="delete-button" @click="deleteComment(comment.id)">
                      <i class="fas fa-trash-alt"></i> 삭제
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isGuideModalOpen" class="modal" @click="closeGuideModal">
      <div class="modal-content guide-modal" @click.stop>
        <div class="modal-header">
          <h2>커뮤니티 이용안내</h2>
        </div>
        <div class="guide-content">
          <div class="guide-section">
            <h3><i class="fas fa-check-circle" style="color: #666"></i> 게시글 작성 규칙</h3>
            <ul>
              <li>타인을 비방하거나 욕설을 포함한 게시글은 작성할 수 없습니다.</li>
              <li>광고성 게시글은 관리자에 의해 삭제될 수 있습니다.</li>
              <li>개인정보 보호를 위해 민감한 정보는 게시하지 말아주세요.</li>
            </ul>
          </div>
          <div class="guide-section">
            <h3><i class="fas fa-exclamation-triangle" style="color: #666"></i> 주의사항</h3>
            <ul>
              <!-- <li>이미지 업로드는 최대 5MB까지 가능합니다.</li> -->
              <li>부적절한 내용은 신고될 수 있으며, 이용이 제한될 수 있습니다.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import api from '@/utils/axios'
import type { AxiosError } from 'axios'

const authStore = useAuthStore()
const articles = ref([])
const selectedArticle = ref(null)
const isCreating = ref(false)
const newArticle = ref({
  title: '',
  content: '',
  image: null,
  category: ''
})
const newComment = ref('')
const editArticle = ref({ title: '', content: '' })
const isEditing = ref(false)

const isAuthenticated = computed(() => authStore.isAuthenticated)

// 게시글 록 조회
const fetchArticles = async () => {
  try {
    const response = await api.get('/api/community/articles/')
    console.log('게시글 목록:', response.data)
    articles.value = response.data
  } catch (error) {
    console.error('게시글 목록 조회 실패:', error)
  }
}

// 게시글 상세 조회
const selectArticle = async (articleId: number) => {
  try {
    const response = await api.get(`/api/community/articles/${articleId}/`)
    console.log('게시글 상세:', response.data)
    selectedArticle.value = response.data
  } catch (error) {
    console.error('게시글 상세 조회 실패:', error)
  }
}

// 게시글 작성
const createArticle = async () => {
  try {
    const formData = new FormData()
    formData.append('title', newArticle.value.title)
    formData.append('content', newArticle.value.content)
    if (newArticle.value.image) {
      formData.append('image', newArticle.value.image)
    }

    const response = await api.post('/api/community/articles/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.status === 201) {
      closeModal()
      fetchArticles() // 게시글 목록 새로고침
    }
  } catch (error) {
    console.error('게시글 작성 실패:', error)
  }
}

// 댓글 작성
const createComment = async () => {
  if (!newComment.value.trim()) return

  try {
    await api.post(`/api/community/articles/${selectedArticle.value.id}/comments/`, {
      content: newComment.value
    })
    await selectArticle(selectedArticle.value.id)
    newComment.value = ''
  } catch (error) {
    console.error('댓글 작성 실패:', error)
    alert('댓글 작성에 실패했습니다.')
  }
}

// 유틸리티 함수들
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const selectedImage = ref(null)
const imagePreview = ref(null)

const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedImage.value = file
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const isCreateModalOpen = ref(false)
const isDetailModalOpen = ref(false)
const isGuideModalOpen = ref(false)

const showCreateModal = () => {
  isCreateModalOpen.value = true
}

const showDetailModal = async (articleId: number) => {
  try {
    const response = await api.get(`/api/community/articles/${articleId}/`)
    selectedArticle.value = response.data
    isDetailModalOpen.value = true
  } catch (error) {
    console.error('게시글 로드 실패:', error)
  }
}

const closeModal = () => {
  isCreateModalOpen.value = false
  isDetailModalOpen.value = false
  selectedArticle.value = null
  newArticle.value = { title: '', content: '', image: null, category: '' }
  newComment.value = ''
}

// 게시글 작성자 확인 computed 속성
const isArticleAuthor = computed(() => {
  console.log('현재 사용자 ID:', authStore.userId)
  console.log('게시글 작성자 ID:', selectedArticle.value?.user)
  return selectedArticle.value?.user === parseInt(authStore.userId)
})

// 댓글 작성자 확인 함수
const isCommentAuthor = (comment: any) => {
  if (!comment || !authStore.userId) return false
  return comment.user === parseInt(authStore.userId)
}

// 게시글 수정 폼 표시
const showEditArticleForm = () => {
  editArticle.value = {
    title: selectedArticle.value.title,
    content: selectedArticle.value.content
  }
  isEditing.value = true
}

// 게시글 수정 취소
const cancelEdit = () => {
  isEditing.value = false
  editArticle.value = { title: '', content: '' }
}

// 게시글 수정
const updateArticle = async () => {
  try {
    await api.put(`/api/community/articles/${selectedArticle.value.id}/`, {
      title: editArticle.value.title,
      content: editArticle.value.content
    })
    await selectArticle(selectedArticle.value.id)
    isEditing.value = false
    await fetchArticles()
  } catch (error) {
    console.error('게시글 수정 실패:', error)
    alert('게시글 수정에 실패했습니다.')
  }
}

// 게시글 삭제
const deleteArticle = async () => {
  if (!confirm('정말로 이 게시글을 삭제하시겠습니까?')) return
  
  try {
    await api.delete(`/api/community/articles/${selectedArticle.value.id}/`)
    closeModal()
    await fetchArticles()
  } catch (error) {
    console.error('게시글 삭제 실패:', error)
    alert('게시글 삭제에 실패했습니다.')
  }
}

// 댓글 삭제
const deleteComment = async (commentId: number) => {
  if (!confirm('정말로 이 댓글을 삭제하시겠습니까?')) return
  
  try {
    await api.delete(`/api/community/comments/${commentId}/`)
    await selectArticle(selectedArticle.value.id)
  } catch (error) {
    console.error('댓글 삭제 실패:', error)
    alert('댓글 삭제에 실패했습니다.')
  }
}

// 카테고리 데이터


const currentCategory = ref('all')

// 카테고리 선택 함수
const selectCategory = async (categoryId: string) => {
  currentCategory.value = categoryId
  try {
    const response = await api.get(`/api/community/articles/?category=${categoryId}`)
    articles.value = response.data
  } catch (error) {
    console.error('카테고리 필터링 실패:', error)
  }
}

// 이용안내 모달 컨트롤
const showGuideModal = () => {
  isGuideModalOpen.value = true
}

// 모달 닫기 함수 수정
const closeGuideModal = () => {
  isGuideModalOpen.value = false
}

// 카테고리별 게시글 필터링
const filteredArticles = computed(() => {
  if (currentCategory.value === 'all') {
    return articles.value
  }
  return articles.value.filter(article => article.category === currentCategory.value)
})

onMounted(() => {
  fetchArticles()
})
</script>
<style lang="scss" scoped>
.article-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background: #f8f9fa;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

  .community-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #e9ecef;

    .community-title {
      h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
      }

      p {
        color: #6c757d;
        font-size: 1.1rem;
      }
    }

    .header-actions {
      display: flex;
      gap: 1rem;
      align-items: center;
    }

    .guide-button {
      padding: 0.7rem 1.5rem;
      background: #fff;
      color: #2c3e50;
      border: 2px solid #2c3e50;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-weight: 500;

      &:hover {
        background: #2c3e50;
        color: white;
      }
    }

    .create-button {
      padding: 0.7rem 1.5rem;
      background: #2c3e50;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      gap: 0.5rem;

      &:hover {
        background: #34495e;
        transform: translateY(-2px);
      }

      &:active {
        transform: translateY(0);
      }
    }
  }

  .category-nav {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 12px;
    overflow-x: auto;

    .category-button {
      padding: 0.8rem 1.5rem;
      background: white;
      border: 1px solid #dee2e6;
      border-radius: 8px;
      color: #495057;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      white-space: nowrap;

      i {
        font-size: 1.1rem;
      }

      .post-count {
        background: #e9ecef;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
      }

      &:hover {
        border-color: #2c3e50;
        color: #2c3e50;
      }

      &.active {
        background: #2c3e50;
        color: white;
        border-color: #2c3e50;

        .post-count {
          background: rgba(255, 255, 255, 0.2);
          color: white;
        }
      }
    }
  }

  .article-list {
    display: grid;
    gap: 1.2rem;

    .article-card {
      display: flex;
      background: white;
      border-radius: 12px;
      padding: 1.5rem;
      cursor: pointer;
      transition: all 0.3s ease;
      border: 1px solid #dee2e6;

      &:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
      }

      .article-info {
        flex: 1;

        h3 {
          font-size: 1.3rem;
          color: #2c3e50;
          margin-bottom: 0.8rem;
          font-weight: 600;
        }

        .article-preview {
          color: #6c757d;
          line-height: 1.6;
          margin-bottom: 1.2rem;
          font-size: 1rem;
        }

        .article-meta {
          display: flex;
          gap: 1.5rem;
          color: #adb5bd;
          font-size: 0.9rem;

          span {
            display: flex;
            align-items: center;
            gap: 0.4rem;

            i {
              font-size: 1rem;
            }
          }
        }
      }

      .article-thumbnail {
        width: 140px;
        height: 140px;
        margin-left: 1.5rem;
        border-radius: 8px;
        overflow: hidden;
        
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.3s ease;

          &:hover {
            transform: scale(1.05);
          }
        }
      }
    }
  }
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  padding: 2rem;
}

.article-actions, .comment-actions {
  display: inline-flex;
  gap: 8px;
  
  button {
    padding: 4px 8px;
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    
    &:hover {
      background-color: #e0e0e0;
    }
  }
}

.article-info {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.edit-form {
  margin: 20px 0;
  
  input, textarea {
    width: 100%;
    margin-bottom: 10px;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  textarea {
    min-height: 200px;
  }
}

.comment {
  .comment-header {
    button {
      padding: 2px 6px;
      font-size: 0.8em;
      background-color: #ff4444;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      
      &:hover {
        background-color: #cc0000;
      }
    }
  }
}

.comment-actions {
  display: inline-flex;
  gap: 8px;
}

.article-list {
  table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    
    thead {
      background: #f8f9fa;
      
      th {
        padding: 1rem;
        font-weight: 600;
        color: #2c3e50;
        text-align: center;
        border-bottom: 2px solid #dee2e6;
        
        &:nth-child(1) { // 번호
          width: 10%;
        }
        &:nth-child(2) { // 제목
          width: 50%;
        }
        &:nth-child(3) { // 작성자
          width: 20%;
        }
        &:nth-child(4) { // 작성일
          width: 20%;
        }
      }
    }
    
    tbody {
      tr {
        cursor: pointer;
        transition: background-color 0.2s ease;
        
        
        &:hover {
          background-color: #f8f9fa;
        }
        
        td {
          padding: 1rem;
          border-bottom: 1px solid #dee2e6;
          
          &:nth-child(1) { // 번호
            color: #6c757d;
            text-align: center;
          }
          
          &:nth-child(2) { // 제목
            color: #2c3e50;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 0;
          }
          
          &:nth-child(3) { // 작성자
            color: #495057;
            text-align: center;
          }
          
          &:nth-child(4) { // 작성일
            color: #6c757d;
            font-size: 0.9rem;
            text-align: center;
          }
        }
      }
    }
  }
}

.create-modal {
  position: relative;
  width: 90%;
  max-width: 800px;
  background: white;
  border-radius: 16px;
  padding: 0;
  overflow: hidden;

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    background: #f8f9fa;
    border-bottom: 1px solid #dee2e6;

    h2 {
      margin: 0;
      font-size: 1.5rem;
      color: #2c3e50;
    }

    .close-button {
      background: none;
      border: none;
      font-size: 1.5rem;
      cursor: pointer;
      color: #6c757d;
      
      &:hover {
        color: #343a40;
      }
    }
  }
}

.article-form, .edit-form {
  padding: 2rem;

  .form-group {
    margin-bottom: 1.5rem;

    label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: 500;
      color: #495057;
    }

    input, textarea {
      width: 100%;
      padding: 0.75rem 1rem;
      border: 1px solid #ced4da;
      border-radius: 8px;
      font-size: 1rem;
      transition: border-color 0.2s ease;

      &:focus {
        outline: none;
        border-color: #b3b3b3;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
      }
    }

    textarea {
      min-height: 200px;
      resize: vertical;
    }
  }

  .file-upload {
    position: relative;
    
    .file-input {
      display: none;
    }

    .file-label {
      display: inline-block;
      padding: 0.5rem 1rem;
      background: #f8f9fa;
      border: 1px solid #dee2e6;
      border-radius: 4px;
      cursor: pointer;
      
      &:hover {
        background: #e9ecef;
      }
    }

    .image-preview {
      margin-top: 1rem;
      display: block;
      
      img {
        max-width: 200px;
        max-height: 200px;
        object-fit: contain;
        border-radius: 4px;
      }
    }
  }
}

.form-buttons {
  position: relative;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  z-index: 1001;

  button {
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;

    &.cancel-button {
      background: #e9ecef;
      border: 1px solid #ced4da;
      color: #495057;
      &:hover {
        background: #dee2e6;
      }
    }

    &.submit-button {
      background: #2c3e50;
      border: none;
      color: white;

      &:hover {
        background: #34495e;
        transform: translateY(-1px);
      }
    }
  }
}

.detail-modal {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  
  .article-content {
    img {
      max-width: 100%;
      height: auto;
    }
  }
  
  .comments-section {
    margin-top: auto;
  }
}

.comment-form {
  position: sticky;
  top: 0;
  background: white;
  padding: 1rem 0;
  z-index: 1;
  border-bottom: 1px solid #eee;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #dee2e6;
  margin-bottom: 2rem;

  .author-info, .date-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #aaaaaa;
    font-size: 0.95rem;

    i {
      color: #5e5e5e;
    }
  }

  .article-actions {
    margin-left: auto;
    display: flex;
    gap: 0.8rem;

    button {
      padding: 0.5rem 1rem;
      border-radius: 6px;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.9rem;
      transition: all 0.2s ease;

      &.edit-button {
        background: #aaaaaa;
        color: white;

        &:hover {
          background: #5e5e5e;
        }
      }

      &.delete-button {
        background: #dc3545;
        color: white;

        &:hover {
          background: #c82333;
        }
      }
    }
  }
}

.article-content {
  margin-bottom: 3rem;
  
  p {
    line-height: 1.8;
    color: #2c3e50;
    font-size: 1.1rem;
    white-space: pre-wrap;
  }

  .article-image {
    margin-top: 1rem;
    
    img {
      max-width: 100%;
      height: auto;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
  }
}

.comments-section {
  h3 {
    font-size: 1.4rem;
    color: #575757;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;

    .comment-count {
      font-size: 1rem;
      background: #e9ecef;
      padding: 0.2rem 0.8rem;
      border-radius: 999px;
      color: #747272;
    }
  }

  .comment-form {
    margin-bottom: 2rem;

    textarea {
      width: 100%;
      padding: 1rem;
      border: 1px solid #dee2e6;
      border-radius: 8px;
      resize: vertical;
      margin-bottom: 1rem;
      font-size: 1rem;
      transition: all 0.2s ease;

      &:focus {
        outline: none;
        border-color: #aaaaaa;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
      }
    }

    .comment-submit {
      padding: 0.8rem 1.5rem;
      background: #7a7a7a;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      float: right;
      transition: all 0.2s ease;

      &:hover {
        background: #5e5e5e;
        transform: translateY(-1px);
      }
    }
  }

  .comments-list {
    .comment {
      padding: 1.5rem;
      border: 1px solid #dee2e6;
      border-radius: 12px;
      margin-bottom: 1rem;
      background: #f8f9fa;

      .comment-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;

        .comment-author {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 500;
          color: #1d1d1d;

          i {
            color: #aaaaaa;
          }
        }

        .comment-date {
          font-size: 0.9rem;
          color: #181818;
        }
      }

      .comment-content {
        p {
          margin: 0;
          line-height: 1.6;
          color: #252525;
        }
      }

      .comment-actions {
        margin-top: 1rem;
        display: flex;
        justify-content: flex-end;

        .delete-button {
          padding: 0.4rem 0.8rem;
          background: #dc3545;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.9rem;
          display: flex;
          align-items: center;
          gap: 0.3rem;
          transition: all 0.2s ease;

          &:hover {
            background: #c82333;
          }
        }
      }
    }
  }
}

.guide-modal {
  max-width: 600px !important;

  .guide-content {
    padding: 2rem;

    .guide-section {
      margin-bottom: 2rem;

      h3 {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;

        i {
          color: #4CAF50;
        }
      }

      ul {
        list-style: none;
        padding: 0;

        li {
          position: relative;
          padding-left: 1.5rem;
          margin-bottom: 0.8rem;
          color: #495057;
          line-height: 1.6;

          &::before {
            content: "•";
            position: absolute;
            left: 0;
            color: #2c3e50;
          }
        }
      }
    }
  }
}

.category-select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 1rem;
  color: #495057;
  background-color: white;
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: #2c3e50;
    box-shadow: 0 0 0 3px rgba(44, 62, 80, 0.1);
  }
}
</style>

