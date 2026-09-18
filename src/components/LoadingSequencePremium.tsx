import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface LoadingSequencePremiumProps {
  progress: number
}

const messages = [
  { text: '📡 Connexion au serveur de l\'amour...', emoji: '💕' },
  { text: '💫 Analyse quantique de compatibilité...', emoji: '⚛️' },
  { text: '🦋 Téléchargement des papillons virtuels...', emoji: '🦋' },
  { text: '😊 Vérification du coefficient de mignonnerie...', emoji: '✨' },
  { text: '💗 Calibrage des fréquences cardiaques...', emoji: '💗' },
  { text: '🎯 Initialisation du protocole romance version 2.0...', emoji: '🔥' },
]

const LoadingSequencePremium: React.FC<LoadingSequencePremiumProps> = ({ progress }) => {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0)
  const [showError, setShowError] = useState(false)

  useEffect(() => {
    if (progress > 40 && progress < 60) {
      setCurrentMessageIndex(1)
    } else if (progress > 60 && progress < 75) {
      setCurrentMessageIndex(2)
    } else if (progress > 75 && progress < 85) {
      setCurrentMessageIndex(3)
    } else if (progress > 85 && progress < 92) {
      setCurrentMessageIndex(4)
    } else if (progress > 92 && progress < 97) {
      setCurrentMessageIndex(5)
    }

    if (progress > 90) {
      setTimeout(() => setShowError(true), 300)
    }
  }, [progress])

  const currentMessage = messages[currentMessageIndex]

  return (
    <div className="min-h-screen flex items-center justify-center px-4 overflow-hidden">
      {/* Animated background */}
      <div className="fixed inset-0 pointer-events-none">
        <motion.div
          className="absolute top-10 right-10 w-96 h-96 bg-rose-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
          animate={{ scale: [1, 1.2, 1], x: [0, 30, 0] }}
          transition={{ duration: 6, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-10 left-10 w-96 h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
          animate={{ scale: [1, 1.1, 1], y: [0, 40, 0] }}
          transition={{ duration: 8, repeat: Infinity, delay: 1 }}
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md relative z-10"
      >
        {/* Logo */}
        <motion.div
          className="text-center mb-12"
          animate={{ scale: [1, 1.1, 1], y: [0, -10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <motion.div
            className="inline-block mb-4"
            animate={{ rotate: 360 }}
            transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
          >
            <div className="text-8xl">❤️</div>
          </motion.div>
          <motion.h1
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="text-4xl font-black text-gradient mb-2"
          >
            Test Ultime
          </motion.h1>
          <p className="text-gray-500 font-semibold">L\'évaluation officielle</p>
        </motion.div>

        {/* Loading bar - Premium */}
        <div className="mb-12">
          <div className="relative">
            <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden shadow-lg">
              <motion.div
                className="h-full bg-gradient-to-r from-rose-500 via-pink-500 to-rose-500"
                animate={{
                  width: `${progress}%`,
                  backgroundPosition: ['0%', '100%'],
                }}
                transition={{
                  width: { duration: 0.3, ease: 'easeOut' },
                  backgroundPosition: { duration: 1, repeat: Infinity },
                }}
              />
            </div>
            <motion.div
              className="absolute top-1/2 -translate-y-1/2 left-0"
              style={{ left: `${progress}%` }}
              animate={{ scale: [1, 1.3, 1] }}
              transition={{ duration: 0.6, repeat: Infinity }}
            >
              <div className="w-6 h-6 rounded-full bg-gradient-to-br from-rose-400 to-pink-500 shadow-lg relative -left-3" />
            </motion.div>
          </div>
          <motion.p
            className="text-center text-sm font-black text-gradient mt-4"
            animate={{ opacity: [0.7, 1, 0.7] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            {Math.round(progress)}%
          </motion.p>
        </div>

        {/* Message */}
        <motion.div
          key={currentMessageIndex}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="text-center mb-8 min-h-16 flex items-center justify-center"
        >
          <div className="space-y-2">
            <motion.p
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="text-4xl"
            >
              {currentMessage.emoji}
            </motion.p>
            <p className="text-gray-700 font-bold text-lg">
              {currentMessage.text}
            </p>
          </div>
        </motion.div>

        {/* Error message */}
        {showError && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-8"
          >
            <div className="bg-gradient-to-br from-red-100 to-orange-100 border-3 border-red-300 rounded-3xl p-6 text-center shadow-2xl">
              <motion.p
                animate={{ rotate: [0, -2, 2, 0] }}
                transition={{ duration: 0.5, repeat: Infinity }}
                className="text-red-700 font-black text-xl mb-2"
              >
                ⚠️ ERREUR SYSTÈME
              </motion.p>
              <p className="text-red-600 font-bold">Code: HEART_OVERFLOW_CRITICAL</p>
              <p className="text-red-500 text-sm mt-2 italic">
                Le système d\'amour a surpassé ses limites normales 💕
              </p>
              <p className="text-red-400 text-xs mt-3">
                (C\'est trop beau pour être vrai... mais ça l\'est 😭)
              </p>
            </div>
          </motion.div>
        )}

        {/* Decorative elements */}
        <motion.div className="flex justify-center gap-4 mt-12">
          {[0, 1, 2, 3, 4].map((i) => (
            <motion.div
              key={i}
              animate={{ y: [0, -20, 0] }}
              transition={{
                duration: 1.2,
                delay: i * 0.15,
                repeat: Infinity,
              }}
              className="text-2xl"
            >
              {i === 0 && '💕'}
              {i === 1 && '✨'}
              {i === 2 && '💫'}
              {i === 3 && '✨'}
              {i === 4 && '💕'}
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </div>
  )
}

export default LoadingSequencePremium
