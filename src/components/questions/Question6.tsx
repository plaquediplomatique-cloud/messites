import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useSound } from '../../hooks/useSound'

interface Question6Props {
  onAnswer: (answer: string) => void
  onEasterEgg: () => void
}

const Question6: React.FC<Question6Props> = ({ onAnswer, onEasterEgg }) => {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const { playSound } = useSound()

  const options = [
    { label: '🔥 "C\'est un mec chaud"', emoji: '🥵' },
    { label: '😍 "Tu es tellement beau"', emoji: '💕' },
    { label: '😂 "Pourquoi tu me fais ça?"', emoji: '💀' },
    { label: '🤨 "Bro c\'est 3h du matin"', emoji: '😴' },
  ]

  const handleAnswer = (answer: string) => {
    playSound('success')
    setSelectedAnswer(answer)
    onEasterEgg()

    setTimeout(() => {
      onAnswer(answer)
    }, 500)
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
          Quelle est ta réaction quand je t'envoie une photo de moi ? 📸
        </p>
      </motion.div>

      {/* Phone mockup */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="mx-auto w-32 h-56 rounded-3xl border-8 border-black bg-white flex items-center justify-center shadow-2xl"
      >
        <motion.div
          animate={{ rotate: [0, -2, 2, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="text-6xl"
        >
          🤳
        </motion.div>
      </motion.div>

      {/* Options */}
      <motion.div
        className="space-y-3"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ staggerChildren: 0.1 }}
      >
        {options.map((option, index) => (
          <motion.button
            key={option.label}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05, x: 8 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleAnswer(option.label)}
            className={`w-full p-4 rounded-2xl font-semibold text-left transition-all ${
              selectedAnswer === option.label
                ? 'bg-gradient-to-r from-rose-500 to-pink-500 text-white shadow-lg'
                : 'bg-white border-2 border-gray-200 text-gray-800 hover:border-rose-300 hover:bg-rose-50'
            }`}
          >
            {option.label}
          </motion.button>
        ))}
      </motion.div>

      {/* Reaction */}
      {selectedAnswer && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card-base p-4 bg-gradient-to-r from-indigo-50 to-blue-50 text-center border-indigo-200"
        >
          <p className="text-gray-700 font-semibold">
            Noté, je dois arrêter les photos à 3h du matin alors 😅
          </p>
        </motion.div>
      )}
    </div>
  )
}

export default Question6
