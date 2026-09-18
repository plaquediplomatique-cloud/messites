import confetti from 'canvas-confetti'

export const triggerConfetti = (intensity: 'light' | 'medium' | 'heavy' = 'medium') => {
  const particleCount = intensity === 'light' ? 50 : intensity === 'medium' ? 150 : 300

  confetti({
    particleCount,
    spread: 70,
    origin: { y: 0.6 },
    colors: ['#ec4899', '#db2777', '#be185d', '#fda4af', '#fbcfe8'],
    gravity: 0.8,
    decay: 0.95,
    startVelocity: intensity === 'light' ? 20 : intensity === 'medium' ? 35 : 45,
  })

  if (intensity === 'heavy') {
    setTimeout(() => {
      confetti({
        particleCount: 100,
        spread: 180,
        origin: { x: 0, y: 0.5 },
        colors: ['#ec4899', '#db2777', '#be185d', '#fda4af', '#fbcfe8'],
        gravity: 0.8,
        decay: 0.95,
        startVelocity: 30,
      })
    }, 200)

    setTimeout(() => {
      confetti({
        particleCount: 100,
        spread: 180,
        origin: { x: 1, y: 0.5 },
        colors: ['#ec4899', '#db2777', '#be185d', '#fda4af', '#fbcfe8'],
        gravity: 0.8,
        decay: 0.95,
        startVelocity: 30,
      })
    }, 400)
  }
}

export const triggerHeartConfetti = () => {
  confetti({
    particleCount: 80,
    spread: 360,
    decay: 0.91,
    scalar: 1.2,
    gravity: 0.5,
    disableForReducedMotion: false,
  })
}
