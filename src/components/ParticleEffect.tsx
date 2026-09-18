import React, { useEffect, useRef } from 'react'

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  opacity: number
  size: number
  type: 'heart' | 'star' | 'sparkle'
}

interface ParticleEffectProps {
  trigger?: boolean
  type?: 'hearts' | 'stars' | 'sparkles' | 'mixed'
  count?: number
}

const ParticleEffect: React.FC<ParticleEffectProps> = ({
  trigger = false,
  type = 'mixed',
  count = 30,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const particlesRef = useRef<Particle[]>([])
  const animationRef = useRef<number | null>(null)

  useEffect(() => {
    if (!trigger || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

    particlesRef.current = []

    for (let i = 0; i < count; i++) {
      const particleType =
        type === 'mixed'
          ? ['heart', 'star', 'sparkle'][Math.floor(Math.random() * 3)]
          : type === 'hearts'
            ? 'heart'
            : type === 'stars'
              ? 'star'
              : 'sparkle'

      particlesRef.current.push({
        x: Math.random() * canvas.width,
        y: canvas.height + 20,
        vx: (Math.random() - 0.5) * 4,
        vy: Math.random() * -3 - 2,
        opacity: Math.random() * 0.5 + 0.5,
        size: Math.random() * 15 + 10,
        type: particleType as 'heart' | 'star' | 'sparkle',
      })
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      for (let i = particlesRef.current.length - 1; i >= 0; i--) {
        const particle = particlesRef.current[i]
        particle.y += particle.vy
        particle.x += particle.vx
        particle.vy += 0.1 // gravity
        particle.opacity -= 0.005

        if (particle.opacity <= 0) {
          particlesRef.current.splice(i, 1)
        } else {
          ctx.globalAlpha = particle.opacity
          drawParticle(ctx, particle)
        }
      }

      if (particlesRef.current.length > 0) {
        animationRef.current = requestAnimationFrame(animate)
      } else {
        ctx.globalAlpha = 1
      }
    }

    animationRef.current = requestAnimationFrame(animate)

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [trigger, type, count])

  const drawParticle = (
    ctx: CanvasRenderingContext2D,
    particle: Particle
  ) => {
    const { x, y, size, type } = particle

    ctx.font = `${size}px Arial`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'

    switch (type) {
      case 'heart':
        ctx.fillText('❤️', x, y)
        break
      case 'star':
        ctx.fillText('⭐', x, y)
        break
      case 'sparkle':
        ctx.fillText('✨', x, y)
        break
    }
  }

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        pointerEvents: 'none',
        zIndex: 40,
      }}
    />
  )
}

export default ParticleEffect
