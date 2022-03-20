<template>
  <div v-if="open" class="w-full h-full flex flex-row">
    <div class="w-1/5 bg-red-500 flex flex-col justify-center p-5">
      <div class="w-full">
        <router-link class="text-3xl font-bold font-sans border-4 border-black rounded p-2 block" :to="{ name: 'Submit' }">Submit</router-link>
      </div>
      <div class="w-full mt-5">
        <router-link class="text-3xl font-bold font-sans border-4 border-black rounded p-2 block" :to="{ name: 'SubmissionValidation' }">Submission Validation</router-link>
      </div>
    </div>
    <div class="w-4/5">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Navigation',
  data() {
    return {
      open: true,
    };
  },
};
</script>

<style scoped>
</style>
