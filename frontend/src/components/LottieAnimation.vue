<template>
  <div ref="animationContainer" :style="{ width: size + 'px', height: size + 'px' }"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import lottie from 'lottie-web'

const props = defineProps({
  animationData: {
    type: Object,
    required: true
  },
  size: {
    type: Number,
    default: 200
  },
  loop: {
    type: Boolean,
    default: true
  },
  autoplay: {
    type: Boolean,
    default: true
  }
})

const animationContainer = ref(null)
let anim = null

onMounted(() => {
  initAnimation()
})

const initAnimation = () => {
  if (animationContainer.value) {
    anim = lottie.loadAnimation({
      container: animationContainer.value,
      renderer: 'svg',
      loop: props.loop,
      autoplay: props.autoplay,
      animationData: props.animationData
    })
  }
}

watch(() => props.animationData, () => {
  if (anim) {
    anim.destroy()
  }
  initAnimation()
}, { deep: true })

onUnmounted(() => {
  if (anim) {
    anim.destroy()
  }
})
</script>
