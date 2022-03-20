import Vue from 'vue';
import { Amplify, Auth } from 'aws-amplify';

import vueAwesomeCountdown from 'vue-awesome-countdown';

import {
  applyPolyfills,
  defineCustomElements,
} from '@aws-amplify/ui-components/loader';

import App from '@/App.vue';

import '@/assets/tailwind.css';
import router from './router';

Vue.config.productionTip = false;

Amplify.configure({
  aws_cloud_logic_custom: [
    {
      endpoint: process.env.VUE_APP_API_DOMAIN_NAME,
      name: 'HttpApi',
      custom_header: async () => {
        const user = await Auth.currentAuthenticatedUser();
        const token = await user.signInUserSession.idToken.jwtToken;

        return {
          Authorization: `${token}`,
          'Content-Type': 'application/json',
        };
      },
    },
  ],
  aws_project_region: process.env.VUE_APP_REGION,
  aws_cognito_region: process.env.VUE_APP_REGION,
  aws_user_pools_id: process.env.VUE_APP_COGNITO_USER_POOL,
  aws_user_pools_web_client_id: process.env.VUE_APP_COGNITO_USER_POOL_CLIENT,
});

applyPolyfills().then(() => {
  defineCustomElements(window);
});

Vue.config.ignoredElements = [/amplify-\w*/];

Vue.use(vueAwesomeCountdown);

new Vue({
  router,
  render: (h) => h(App),
}).$mount('#app');
