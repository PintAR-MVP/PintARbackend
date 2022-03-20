<template>
  <div class="flex flex-col items-center px-5">
    <div class="my-5 w-full">
      <div class="inline mr-2 font-bold font-sans text-2xl">Name: </div>
      <input v-model="internalProduct.name" type="text">
    </div>
    <div class="my-5 w-full">
      <div class="inline mr-2 font-bold font-sans text-2xl">Category: </div>
      <input v-model="internalProduct.category" type="text">
    </div>
    <div class="my-5 w-full flex flex-col items-center">
      <div class="mb-2 w-full font-bold font-sans text-2xl">Images:</div>
      <ImageEditor v-if="internalProduct.images.length > 0" ref="editor" class="max-w-full" :src="internalProduct.images[currentImageIndex]"></ImageEditor>
      <div class="w-full flex flex-row items-center justify-start pt-2">
        <div v-if="!drawing">
          <button  class="p-1 border-2 border-black rounded font-bold font-sans text-base" @click="drawShape">Draw Shape</button>
        </div>
        <div v-else class="mr-2">
          <button class="p-1 mr-2 border-2 border-black rounded font-bold font-sans text-base" @click="saveShape">Save Shape</button>
          <button class="p-1 ml-2 border-2 border-black rounded font-bold font-sans text-base" @click="discardShape">Discard Shape</button>
        </div>
        <div class="mr-auto ml-2">
          <button class="p-1 border-2 border-black rounded font-bold font-sans text-base" @click="saveColor">Save Color</button>
        </div>
        <div class="flex flex-row align-center mr-auto">
          <div class="mr-2">
            <button class="p-1 border-2 border-black rounded font-bold font-sans text-base" @click="prevImage">Previous</button>
          </div>
          <div class="mx-2 font-bold font-sans text-lg">{{currentImageIndex + 1}} / {{internalProduct.images.length}}</div>
          <div class="ml-2">
            <button class="p-1 border-2 border-black rounded font-bold font-sans text-base" @click="nextImage">Next</button>
          </div>
        </div>
        <div class="ml-auto mr-2">
          <input @input="uploadImage" class="hidden" ref="imageInput" type="file" accepts="image/jpeg, image/png">
          <button class="p-1 mr-2 border-2 border-black rounded font-bold font-sans text-base" @click="$refs.imageInput.click()">Upload</button>
          <button class="p-1 ml-2 border-2 border-black rounded font-bold font-sans text-base" @click="deleteImage">Delete</button>
        </div>
      </div>
    </div>
    <div class="m-5 w-full">
      <div class="mb-2 w-full font-bold font-sans text-2xl">Label Text:</div>
      <textarea class="w-full" v-model="internalProduct.label_text" rows="10" type="text"/>
    </div>
    <div class="my-5 w-full">
      <div class="mb-2 w-full font-bold font-sans text-2xl">Shape:</div>
      <textarea class="w-full" v-model="internalProduct.shape" rows="3" type="text"/>
    </div>
    <div class="my-5 w-full">
      <div class="inline mr-2 font-bold font-sans text-2xl">Color: </div>
      <input v-model="internalProduct.color" type="text">
    </div>
  </div>
</template>

<script>
import ImageEditor from '@/components/ImageEditor.vue';

export default {
  props: {
    product: Object,
  },
  components: {
    ImageEditor,
  },
  data() {
    return {
      internalProduct: null,
      currentImageIndex: 0,
      drawing: false,
    };
  },
  async created() {
    this.internalProduct = JSON.parse(JSON.stringify(this.product));
  },
  methods: {
    drawShape() {
      this.drawing = true;
      this.$refs.editor.startDrawing();
    },
    saveShape() {
      this.internalProduct.shape = this.$refs.editor.saveDrawShapeAsWKT();
      this.drawing = false;
      this.$refs.editor.resetDrawing();
      this.$refs.editor.endDrawing();
    },
    discardShape() {
      this.$refs.editor.resetDrawing();
    },
    saveColor() {
      this.internalProduct.color = this.$refs.editor.getAverageColor();
    },
    prevImage() {
      if (this.currentImageIndex > 0) {
        this.currentImageIndex -= 1;
      }
    },
    nextImage() {
      if (this.currentImageIndex + 1 < this.internalProduct.images.length) {
        this.currentImageIndex += 1;
      }
    },
    uploadImage(event) {
      const image = event.target.files[0];
      if (image) {
        const reader = new FileReader();

        reader.addEventListener('load', () => {
          this.internalProduct.images.push(reader.result);
        }, false);

        reader.readAsDataURL(image);
      }
    },
    deleteImage() {
      this.internalProduct.images = this.internalProduct.images.filter((x, i) => i !== this.currentImageIndex);
      if (this.currentImageIndex >= this.internalProduct.images.length) {
        this.currentImageIndex = Math.max(this.internalProduct.images.length - 1, 0);
      }
    },
    async save() {
      const result = {};
      result.name = `${this.internalProduct.name}`;
      result.category = `${this.internalProduct.category}`;
      result.label_text = `${this.internalProduct.label_text}`;
      result.color = `${this.internalProduct.color}`;
      result.shape = `${this.internalProduct.shape}`;
      result.images = await Promise.all(
        this.internalProduct.images.map(
          (image) => new Promise((fulfilled) => {
            const img = new Image();
            img.setAttribute('crossOrigin', 'anonymous');
            img.onload = () => {
              const canvas = document.createElement('canvas');
              canvas.width = img.width;
              canvas.height = img.height;

              const ctx = canvas.getContext('2d');
              ctx.drawImage(img, 0, 0);

              const dataURL = canvas.toDataURL('image/jpeg', 0.90);

              fulfilled(dataURL);
            };
            img.src = image;
          }),
        ),
      );

      return result;
    },
  },
};
</script>

<style scoped>
</style>
