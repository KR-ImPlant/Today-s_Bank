// src/router/index.ts
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import HomeView from '@/views/HomeView.vue';
import ProductView from '@/views/ProductsView.vue';
import CommunityView from '@/views/CommunityView.vue';
import RecommendationView from '@/views/RecommendationView.vue';
import UserProfileView from '@/views/UserProfileView.vue';
import BankView from '@/views/BankView.vue';
import ExchangeView from '@/views/ExchangeView.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/product',
    name: 'product',
    component: ProductView,
  },
  {
    path: '/map',
    name: 'bank-map',
    component: BankView,
  },
  {
    path: '/exchange',
    name: 'exchange-calculator',
    component: ExchangeView,
  },
  {
    path: '/community',
    name: 'community',
    component: CommunityView,
  },
  {
    path: '/recommendation',
    name: 'recommendation',
    component: RecommendationView,
    children: [
      {
        path: '',
        redirect: '/recommendation/1'
      },
      {
        path: ':step(\\d+)',
        name: 'recommendation-step',
        component: () => import('@/views/RecommendationView.vue')
      },
      {
        path: 'result',
        name: 'recommendation-result',
        component: () => import('@/views/RecommendationView.vue')
      }
    ],
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: UserProfileView,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// Navigation guard
router.beforeEach(async (to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const auth = useAuthStore();
    
    if (!auth.isAuthenticated) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
