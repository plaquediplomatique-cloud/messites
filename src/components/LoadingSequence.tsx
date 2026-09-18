import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface LoadingSequenceProps {
  progress: number
}

const messages = [
  '📡 Connexion au serveur de l\'amour...',
  '💫 Analyse de la compatibilité...',
  '🦋 Téléchargement des papillons...',
  '😊 Vérification du niveau de mignonnerie...',
  '💕 Calibrage des sentiments...',
  '🎯 Initialisation du mode romance...',
]

const LoadingSequence: React.FC<LoadingSequenceProps> = ({ progress }) => {
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

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <motion.div
          className="text-center mb-12"
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="text-6xl mb-4">❤️</div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Test de Compatibilité</h1>
        </motion.div>

        {/* Loading bar */}
        <div className="mb-8 space-y-4">
          <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-rose-500 via-pink-500 to-rose-500"
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3, ease: 'easeOut' }}
            />
          </div>
          <p className="text-center text-sm font-semibold text-gray-600">
            {Math.round(progress)}%
          </p>
        </div>

        {/* Messages */}
        <motion.div
          key={currentMessageIndex}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="text-center mb-8 h-8 flex items-center justify-center"
        >
          <p className="text-gray-600 font-medium">{messages[currentMessageIndex]}</p>
        </motion.div>

        {/* Error message */}
        {showError && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="mb-8"
          >
            <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-4 text-center">
              <p className="text-red-600 font-bold text-sm">⚠️ Erreur détectée</p>
              <p className="text-red-500 text-xs mt-1">
                Code d'erreur : HEART_OVERFLOW_404
              </p>
              <p className="text-red-400 text-xs mt-2 italic">
                (C'est trop beau pour être vrai, en fait ça l'est 😭)
              </p>
            </div>
          </motion.div>
        )}

        {/* Decorative elements */}
        <div className="flex justify-center gap-3 mt-12">
          {[0, 1, 2].map(i => (
            <motion.div
              key={i}
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 1.5, delay: i * 0.2, repeat: Infinity }}
              className="text-2xl"
            >
              {i === 0 ? '💕' : i === 1 ? '✨' : '💫'}
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default LoadingSequence
