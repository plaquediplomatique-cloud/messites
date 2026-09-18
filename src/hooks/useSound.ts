export const useSound = () => {
  const playSound = (
    type: 'click' | 'success' | 'error' | 'ding' | 'ambient' | 'fart' | 'dab' | 'bruh' | 'fail' | 'cringe'
  ) => {
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
          osc.frequency.value = 650
          gain.gain.setValueAtTime(0.12, now)
          gain.gain.exponentialRampToValueAtTime(0.01, now + 0.12)
          osc.start(now)
          osc.stop(now + 0.12)
          break
        }
        case 'success': {
          const notes = [880, 1100, 1320]
          notes.forEach((freq, i) => {
            const osc = audioContext.createOscillator()
            const gain = audioContext.createGain()
            osc.connect(gain)
            gain.connect(audioContext.destination)
            osc.frequency.value = freq
            gain.gain.setValueAtTime(0.12, now + i * 0.08)
            gain.gain.exponentialRampToValueAtTime(0.01, now + i * 0.08 + 0.15)
            osc.start(now + i * 0.08)
            osc.stop(now + i * 0.08 + 0.15)
          })
          break
        }
        case 'ding': {
          const osc = audioContext.createOscillator()
          const gain = audioContext.createGain()
          osc.connect(gain)
          gain.connect(audioContext.destination)
          osc.frequency.setValueAtTime(1400, now)
          osc.frequency.exponentialRampToValueAtTime(700, now + 0.4)
          gain.gain.setValueAtTime(0.15, now)
          gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4)
          osc.start(now)
          osc.stop(now + 0.4)
          break
        }
        case 'error': {
          const osc = audioContext.createOscillator()
          const gain = audioContext.createGain()
          osc.connect(gain)
          gain.connect(audioContext.destination)
          osc.frequency.setValueAtTime(350, now)
          osc.frequency.exponentialRampToValueAtTime(150, now + 0.4)
          gain.gain.setValueAtTime(0.15, now)
          gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4)
          osc.start(now)
          osc.stop(now + 0.4)
          break
        }
        case 'fart': {
          // Bruit de pet goofy
          const noise = audioContext.createBufferSource()
          const buffer = audioContext.createBuffer(1, audioContext.sampleRate * 0.3, audioContext.sampleRate)
          const data = buffer.getChannelData(0)
          for (let i = 0; i < buffer.length; i++) {
            data[i] = Math.random() * 2 - 1
          }
          const gain = audioContext.createGain()
          noise.buffer = buffer
          noise.connect(gain)
          gain.connect(audioContext.destination)
          gain.gain.setValueAtTime(0.08, now)
          gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3)
          noise.start(now)
          noise.stop(now + 0.3)
          break
        }
        case 'bruh': {
          // Son "bruh" style airhorn
          const osc = audioContext.createOscillator()
          const gain = audioContext.createGain()
          osc.connect(gain)
          gain.connect(audioContext.destination)
          osc.frequency.setValueAtTime(200, now)
          osc.frequency.linearRampToValueAtTime(100, now + 0.15)
          gain.gain.setValueAtTime(0.2, now)
          gain.gain.linearRampToValueAtTime(0.01, now + 0.15)
          osc.start(now)
          osc.stop(now + 0.15)
          break
        }
        case 'dab': {
          // Son de "dab" genre airhorn court et sec
          const osc = audioContext.createOscillator()
          const gain = audioContext.createGain()
          osc.connect(gain)
          gain.connect(audioContext.destination)
          osc.frequency.setValueAtTime(900, now)
          osc.frequency.exponentialRampToValueAtTime(600, now + 0.2)
          gain.gain.setValueAtTime(0.2, now)
          gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2)
          osc.start(now)
          osc.stop(now + 0.2)
          break
        }
        case 'fail': {
          // Bruit d'échec classique
          const freq1 = 500,
            freq2 = 300
          for (let i = 0; i < 2; i++) {
            const osc = audioContext.createOscillator()
            const gain = audioContext.createGain()
            osc.connect(gain)
            gain.connect(audioContext.destination)
            osc.frequency.value = i === 0 ? freq1 : freq2
            gain.gain.setValueAtTime(0.08, now + i * 0.15)
            gain.gain.exponentialRampToValueAtTime(0.01, now + i * 0.15 + 0.2)
            osc.start(now + i * 0.15)
            osc.stop(now + i * 0.15 + 0.2)
          }
          break
        }
        case 'cringe': {
          // Son de cringe absurde
          const notes = [1200, 800, 600]
          notes.forEach((freq, i) => {
            const osc = audioContext.createOscillator()
            const gain = audioContext.createGain()
            osc.connect(gain)
            gain.connect(audioContext.destination)
            osc.frequency.value = freq
            gain.gain.setValueAtTime(0.08, now + i * 0.08)
            gain.gain.exponentialRampToValueAtTime(0.01, now + i * 0.08 + 0.12)
            osc.start(now + i * 0.08)
            osc.stop(now + i * 0.08 + 0.12)
          })
          break
        }
      }
    } catch {
      // Audio context not available
    }
  }

  return { playSound }
}
