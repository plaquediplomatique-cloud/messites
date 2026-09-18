import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useSound } from '../../hooks/useSound'

interface Question2Props {
  onAnswer: (answer: string) => void
  onEasterEgg: () => void
}

const Question2: React.FC<Question2Props> = ({ onAnswer, onEasterEgg }) => {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const { playSound } = useSound()

  const options = [
    { label: 'Oui ❤️', emoji: '😍' },
    { label: 'Absolument', emoji: '🔥' },
    { label: 'Évidemment', emoji: '😎' },
    { label: 'Je refuse de répondre', emoji: '🤐' },
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
          Est-ce que je suis le plus beau mec que tu connaisses ? ✨
        </p>
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
            className={`w-full p-4 rounded-2xl font-bold text-lg transition-all ${
              selectedAnswer === option.label
                ? 'bg-gradient-to-r from-rose-500 to-pink-500 text-white shadow-lg'
                : 'bg-white border-2 border-gray-200 text-gray-800 hover:border-rose-300 hover:bg-rose-50'
            }`}
          >
            <span className="mr-3">{option.emoji}</span>
            {option.label}
          </motion.button>
        ))}
      </motion.div>

      {/* Reaction based on answer */}
      {selectedAnswer && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card-base p-4 bg-gradient-to-r from-purple-50 to-pink-50 text-center"
        >
          {selectedAnswer === 'Je refuse de répondre' ? (
            <p className="text-gray-700 font-semibold">Haha, réponse acceptée 😏</p>
          ) : (
            <p className="text-gray-700 font-semibold">Tu as du goût, merci 💕</p>
          )}
        </motion.div>
      )}
    </div>
  )
}

export default Question2
