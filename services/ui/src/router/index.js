import Vue from 'vue';
import VueRouter from 'vue-router';

import Navigation from '@/views/Navigation.vue';
import SubmissionValidation from '@/views/SubmissionValidation.vue';
import Submit from '@/views/Submit.vue';

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'Navigation',
    component: Navigation,
    children: [
      {
        path: '/submission-validation',
        name: 'SubmissionValidation',
        component: SubmissionValidation,
      },
      {
        path: '/submit',
        name: 'Submit',
        component: Submit,
      },
      {
        path: '',
        name: 'Submit',
        component: Submit,
      },
    ],
  },
];

const router = new VueRouter({
  routes,
});

export default router;
