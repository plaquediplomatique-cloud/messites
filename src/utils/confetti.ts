import confetti from 'canvas-confetti'

// canvas-confetti renders into a full-viewport fixed canvas with a very
// high default z-index (100), which sits on top of everything — including
// content that appears *after* the burst (e.g. the contract/result screens
// that follow a celebration). Pinning it below our screen content's
// z-10 keeps the confetti as a nice background flourish instead of a
// wall that hides the UI for several seconds.
const CONFETTI_Z_INDEX = 5

export const triggerConfetti = (intensity: 'light' | 'medium' | 'heavy' = 'medium') => {
  const particleCount = intensity === 'light' ? 40 : intensity === 'medium' ? 90 : 160

  confetti({
    particleCount,
    spread: 70,
    origin: { y: 0.6 },
    colors: ['#ec4899', '#db2777', '#be185d', '#fda4af', '#fbcfe8'],
    gravity: 1,
    decay: 0.92,
    startVelocity: intensity === 'light' ? 20 : intensity === 'medium' ? 30 : 40,
    zIndex: CONFETTI_Z_INDEX,
  })

  if (intensity === 'heavy') {
    setTimeout(() => {
      confetti({
        particleCount: 60,
        spread: 150,
        origin: { x: 0, y: 0.5 },
        colors: ['#ec4899', '#db2777', '#be185d', '#fda4af', '#fbcfe8'],
        gravity: 1,
        decay: 0.92,
        startVelocity: 28,
        zIndex: CONFETTI_Z_INDEX,
      })
    }, 200)

    setTimeout(() => {
      confetti({
        particleCount: 60,
        spread: 150,
        origin: { x: 1, y: 0.5 },
        colors: ['#ec4899', '#db2777', '#be185d', '#fda4af', '#fbcfe8'],
        gravity: 1,
        decay: 0.92,
        startVelocity: 28,
        zIndex: CONFETTI_Z_INDEX,
      })
    }, 400)
  }
}

export const triggerHeartConfetti = () => {
  confetti({
    particleCount: 50,
    spread: 360,
    decay: 0.9,
    scalar: 1.1,
    gravity: 0.7,
    disableForReducedMotion: false,
    zIndex: CONFETTI_Z_INDEX,
  })
}
