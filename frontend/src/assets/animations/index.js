// 简化的动画数据（使用CSS动画替代Lottie）
// 这些可以在后期替换为真实的Lottie动画数据

export const starAnimation = {
  // 星星闪烁动画
  starTwinkle: {
    // 后续可以用真实的Lottie JSON数据替换
    type: 'css',
    animation: 'twinkle'
  },

  // 星星飞入动画
  starFlyIn: {
    type: 'css',
    animation: 'flyIn'
  }
}

export const confettiAnimation = {
  // 撒花动画
  confetti: {
    type: 'css',
    animation: 'fall'
  }
}

export const letterAnimation = {
  // 字母弹出动画
  letterPop: {
    type: 'css',
    animation: 'pop'
  }
}

export const successAnimation = {
  // 成功庆祝动画
  celebrate: {
    type: 'css',
    animation: 'bounce'
  }
}

// CSS动画类
export const cssAnimations = `
@keyframes twinkle {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

@keyframes flyIn {
  0% { transform: translateY(-100px) scale(0); opacity: 0; }
  50% { transform: translateY(0) scale(1.2); opacity: 1; }
  100% { transform: translateY(0) scale(1); opacity: 1; }
}

@keyframes fall {
  0% { transform: translateY(-100vh) rotate(0deg); opacity: 1; }
  100% { transform: translateY(100vh) rotate(360deg); opacity: 0; }
}

@keyframes pop {
  0% { transform: scale(0) rotate(-180deg); }
  50% { transform: scale(1.2) rotate(0deg); }
  100% { transform: scale(1) rotate(0deg); }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-twinkle {
  animation: twinkle 1s ease-in-out infinite;
}

.animate-fly-in {
  animation: flyIn 0.8s ease-out forwards;
}

.animate-fall {
  animation: fall 3s linear forwards;
}

.animate-pop {
  animation: pop 0.8s ease-out forwards;
}

.animate-bounce {
  animation: bounce 1s ease-in-out;
`
