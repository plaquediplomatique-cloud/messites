import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useSound } from '../../hooks/useSound'

interface Question5Props {
  onAnswer: (answer: number) => void
  onEasterEgg: () => void
}

const Question5: React.FC<Question5Props> = ({ onAnswer, onEasterEgg }) => {
  const [kisses, setKisses] = useState(0)
  const [hasAnswered, setHasAnswered] = useState(false)
  const { playSound } = useSound()

  useEffect(() => {
    if (!hasAnswered) {
      const interval = setInterval(() => {
        setKisses(prev => {
          const next = prev + 1
          if (next % 50 === 0) {
            playSound('ding')
          }
          return next
        })
      }, 120)

      return () => clearInterval(interval)
    }
  }, [hasAnswered, playSound])

  const handleSubmit = () => {
    playSound('success')
    setHasAnswered(true)
    onEasterEgg()

    setTimeout(() => {
      onAnswer(kisses)
    }, 800)
  }

  return (
    <div className="space-y-6">
      {/* Question */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-base p-6 text-center"
      >
        <p className="text-2xl font-black text-gray-800">
          Combien de bisous me dois-tu ? 💋
        </p>
      </motion.div>

      {/* Counter card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        className="card-base bg-gradient-to-br from-white/80 to-rose-50/80 p-12 text-center"
      >
        <motion.div
          key={kisses}
          animate={{
            scale: [1, 1.3, 1],
            rotate: kisses > 200 ? [0, -8, 8, 0] : 0
          }}
          transition={{ duration: 0.2 }}
          className="text-8xl font-black text-gradient mb-4 drop-shadow-lg"
        >
          {kisses}
        </motion.div>

        <motion.p
          key={`msg-${Math.floor(kisses / 25)}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-gray-700 font-bold mb-6 text-lg"
        >
          {kisses === 0 && "⏳ La machine de l'amour démarre..."}
          {kisses > 0 && kisses < 25 && "📈 C'est un bon début..."}
          {kisses >= 25 && kisses < 50 && '🚀 Ça monte fort là!'}
          {kisses >= 50 && kisses < 100 && "⚡ HOLD UP C'est DEU! 😭"}
          {kisses >= 100 && kisses < 200 && "💀 T'ES SÉRIEUSE LÀ??? STOP!"}
          {kisses >= 200 && "🌟 OK C'EST L'INFINI MAINTENANT TU M'TUES"}
        </motion.p>

        {!hasAnswered && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSubmit}
            className="btn-primary-rose"
          >
            Arrêter le compteur
          </motion.button>
        )}

        {hasAnswered && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-sm text-gray-600 font-semibold"
          >
            <p className="mb-2">✓ Total enregistré</p>
            <p className="text-xs text-gray-500">
              Je vais devoir être très bisouille 😘
            </p>
          </motion.div>
        )}
      </motion.div>

      {/* Decoration */}
      <motion.div className="flex justify-center gap-2 text-3xl">
        {Array.from({ length: Math.min(5, Math.floor(kisses / 20)) }).map((_, i) => (
          <motion.span
            key={i}
            animate={{ y: [0, -10, 0] }}
            transition={{ delay: i * 0.1, duration: 1, repeat: Infinity }}
          >
            💋
          </motion.span>
        ))}
      </motion.div>
    </div>
  )
}

export default Question5
