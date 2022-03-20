<template>
  <div class="w-full h-full bg-green-400 overflow-x-hidden overflow-y-auto">
    <div v-if="loading" class="w-full h-full flex flex-col">
      <div class="font-bold font-sans text-6xl mb-auto">Submission Validation</div>
        <div class="font-bold font-sans text-xl mb-auto flex flex-col">
          Loading...
        </div>
        <div class="flex flex-row">
          <div class="ml-auto flex flex-row">
            <div class="flex flex-col items-center justify-items-center">
              <div class="mt-auto relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                <input v-model="autoRefresh" type="checkbox" name="toggle" id="toggle" class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"/>
                <label for="toggle" class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
              </div>
              <div class="mb-auto font-bold font-sans">auto refresh</div>
            </div>
            <div>
              <button disabled class="cursor-not-allowed m-2 font-bold font-sans text-xl p-2 border-2 border-black rounded font-bold font-sans text-3xl">Refresh</button>
            </div>
          </div>
        </div>
    </div>
    <div v-else class="w-full h-full">
      <div v-if="status === 200" class="w-full h-full flex flex-col">
        <div class="font-bold font-sans text-6xl mb-5">Submission Validation</div>
        <div class="font-bold font-sans text-3xl mb-5">
          <countdown @finish="timeout" :end-time="new Date().getTime() + (10 * 60 * 1000)">
            <template v-slot:process="{ timeObj }">
              <div :class="{'text-red-500': timeObj.m < 3, 'animate-pulse': timeObj.m < 1 }">Session {{timeObj.m}}:{{timeObj.s}}</div>
            </template>
          </countdown>
        </div>
        <ProductEditor class="w-full mt-auto" ref="editor" :product="product"></ProductEditor>
        <div class="w-full flex flex-row mt-auto">
          <div>
            <button class="m-2 p-2 border-2 border-black rounded font-bold font-sans text-3xl" @click="createProduct">Create Product</button>
          </div>
          <div>
            <button class="m-2 p-2 border-2 border-black rounded font-bold font-sans text-3xl" @click="deleteJob">Discard Data</button>
          </div>
          <div class="ml-auto flex flex-row">
            <div class="flex flex-col items-center justify-items-center">
              <div class="mt-auto relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                <input v-model="autoRefresh" type="checkbox" name="toggle" id="toggle" class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"/>
                <label for="toggle" class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
              </div>
              <div class="mb-auto font-bold font-sans">auto refresh</div>
            </div>
            <div>
              <button class="m-2 font-bold font-sans text-xl p-2 border-2 border-black rounded font-bold font-sans text-3xl" @click="getJob"> Refresh </button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="w-full h-full flex flex-col">
        <div class="font-bold font-sans text-6xl mb-auto">Submission Validation</div>
        <div class="font-bold font-sans text-xl mb-auto flex flex-col">
          Refresh for jobs
        </div>
        <div class="flex flex-row">
          <div class="ml-auto flex flex-row">
            <div class="flex flex-col items-center justify-items-center">
              <div class="mt-auto relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                <input v-model="autoRefresh" type="checkbox" name="toggle" id="toggle" class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"/>
                <label for="toggle" class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
              </div>
              <div class="mb-auto font-bold font-sans">auto refresh</div>
            </div>
            <div>
              <button class="m-2 font-bold font-sans text-xl p-2 border-2 border-black rounded font-bold font-sans text-3xl" @click="getJob"> Refresh </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { API } from 'aws-amplify';
import axios from 'axios';

import ProductEditor from '@/components/ProductEditor.vue';

export default {
  name: 'SubmissionValidation',
  components: {
    ProductEditor,
  },
  data() {
    return {
      loading: false,
      status: null,
      id: null,
      autoRefresh: false,
      product: {},
    };
  },
  methods: {
    timeout() {
      this.status = null;
      this.id = null;
      this.product = {};
    },
    async getJob() {
      this.loading = true;

      try {
        const response = await API.get('HttpApi', '/submit/validate', { response: true });

        this.status = response.status;
        if (this.status === 200) {
          this.id = response.data.task_id;
          this.product = response.data.task_data;
        }
      } catch (err) {
        console.err(err);
      }

      this.loading = false;
    },
    async deleteJob() {
      await API.del('HttpApi', '/submit/validate', {
        body: {
          task_id: this.id,
        },
      });

      this.status = null;
      this.id = null;
      this.product = {};

      if (this.autoRefresh) {
        await this.getJob();
      }
    },
    async createProduct() {
      const product = await this.$refs.editor.save();

      const images = await Promise.all(product.images.map((image) => fetch(image).then((res) => res.blob())));
      console.log(images);

      const response = await API.post('HttpApi', '/submit/product-image', { body: { count: images.length } });

      const imageUploadUrls = response.images.map((x) => x.upload_url);
      const imageUploads = images.map((image, i) => {
        const imageUploadUrl = imageUploadUrls[i];

        return axios.put(imageUploadUrl, image, {
          headers: {
            'Content-Type': image.type,
          },
        });
      });

      await Promise.all(imageUploads);

      const imageKeys = response.images.map((x) => x.key);

      const createdProduct = await API.post('HttpApi', '/products', {
        body: {
          images: imageKeys,
          name: product.name,
          shape: product.shape,
          label_text: product.label_text,
          category: product.category,
          color: product.color,
        },
      });

      console.log(createdProduct);

      this.deleteJob();
    },
  },
};
</script>

<style scoped>
.toggle-checkbox:checked {
  @apply: right-0 border-green-400;
  right: 0;
  border-color: #e09d28;
}
.toggle-checkbox:checked + .toggle-label {
  @apply: bg-green-400;
  background-color: #e09d28;
}
</style>
