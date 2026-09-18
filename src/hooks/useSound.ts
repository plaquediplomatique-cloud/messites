export const useSound = () => {
  const playSound = (type: 'click' | 'success' | 'error' | 'ding' | 'ambient') => {
    if (typeof window === 'undefined') return

    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      const now = audioContext.currentTime

      switch (type) {
        case 'click': {
          const osc = audioContext.createOscillator()
          const gain = audioContext.createGain()
          osc.connect(gain)
          gain.connect(audioContext.destination)
          osc.frequency.value = 600
          gain.gain.setValueAtTime(0.1, now)
          gain.gain.exponentialRampToValueAtTime(0.01, now + 0.1)
          osc.start(now)
          osc.stop(now + 0.1)
          break
        }
        case 'success': {
          const notes = [800, 1000, 1200]
          notes.forEach((freq, i) => {
            const osc = audioContext.createOscillator()
            const gain = audioContext.createGain()
            osc.connect(gain)
            gain.connect(audioContext.destination)
            osc.frequency.value = freq
            gain.gain.setValueAtTime(0.1, now + i * 0.1)
            gain.gain.exponentialRampToValueAtTime(0.01, now + i * 0.1 + 0.2)
            osc.start(now + i * 0.1)
            osc.stop(now + i * 0.1 + 0.2)
          })
          break
        }
        case 'ding': {
          const osc = audioContext.createOscillator()
          const gain = audioContext.createGain()
          osc.connect(gain)
          gain.connect(audioContext.destination)
          osc.frequency.setValueAtTime(1200, now)
          osc.frequency.exponentialRampToValueAtTime(600, now + 0.5)
          gain.gain.setValueAtTime(0.15, now)
          gain.gain.exponentialRampToValueAtTime(0.01, now + 0.5)
          osc.start(now)
          osc.stop(now + 0.5)
          break
        }
        case 'error': {
          const osc = audioContext.createOscillator()
          const gain = audioContext.createGain()
          osc.connect(gain)
          gain.connect(audioContext.destination)
          osc.frequency.setValueAtTime(400, now)
          osc.frequency.exponentialRampToValueAtTime(200, now + 0.3)
          gain.gain.setValueAtTime(0.1, now)
          gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3)
          osc.start(now)
          osc.stop(now + 0.3)
          break
        }
      }
    } catch {
      // Audio context not available
    }
  }

  return { playSound }
}
