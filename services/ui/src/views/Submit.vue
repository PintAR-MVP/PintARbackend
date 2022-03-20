<template>
  <div class="w-full h-full flex flex-col bg-yellow-400 overflow-x-hidden overflow-y-auto">
    <div class="font-bold font-sans text-6xl mb-5">Submit Product</div>
    <div v-show="!loading" class="flex flex-col mt-auto">
      <div class="mb-5 flex flex-row justify-center align-center">
        <div class="font-bold font-sans text-2xl mr-2">Images:</div>
        <div>
          <input class="hidden" ref="images" type="file" multiple="" accept="image/jpeg, image/png" @change="images = $event.target.files"/>
          <button class="p-1 border-2 border-black rounded font-bold font-sans text-base" @click="$refs.images.click()">Select</button>
        </div>
      </div>
    </div>
    <div v-show="loading" class="flex flex-col mt-auto">
      <div class="font-bold font-sans text-xl mb-auto flex flex-col">
        Loading...
      </div>
    </div>
    <div class="w-full flex flex-row justify-end mt-auto">
      <div>
        <button class="m-2 p-2 border-2 border-black rounded font-bold font-sans text-3xl" @click="upload">Upload</button>
      </div>
    </div>
  </div>
</template>

<script>
import { API } from 'aws-amplify';
import axios from 'axios';

export default {
  name: 'Upload',
  data() {
    return {
      images: null,
      loading: false,
    };
  },
  methods: {
    async upload() {
      this.loading = true;

      const images = Array.from(this.images);

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

      await API.post('HttpApi', '/submit/product', {
        body: {
          images: imageKeys,
        },
      });

      this.images = null;
      this.$refs.images.files = null;
      this.$refs.images.value = null;

      this.loading = false;
    },
  },
};
</script>

<style scoped>
</style>
