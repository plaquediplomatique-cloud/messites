import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useSound } from '../../hooks/useSound'

interface Question2Props {
  onAnswer: (answer: string) => void
  onEasterEgg: () => void
}

const reactions = {
  'Oui ❤️': {
    text: 'Merci à toi 🥺💕',
    emoji: '😭',
    color: 'from-red-100 to-pink-100',
  },
  Absolument: {
    text: 'C\'est fou ça 🔥',
    emoji: '🤩',
    color: 'from-orange-100 to-yellow-100',
  },
  Évidemment: {
    text: 'Basé et redpillé 💯',
    emoji: '😎',
    color: 'from-blue-100 to-purple-100',
  },
  'Je refuse de répondre': {
    text: 'Haha j\'comprends 🤐',
    emoji: '🤫',
    color: 'from-gray-100 to-slate-100',
  },
}

const Question2: React.FC<Question2Props> = ({ onAnswer, onEasterEgg }) => {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const { playSound } = useSound()

  const options = [
    { label: 'Oui ❤️', emoji: '😍', color: 'from-red-400 to-pink-500' },
    { label: 'Absolument', emoji: '🔥', color: 'from-orange-400 to-yellow-500' },
    { label: 'Évidemment', emoji: '😎', color: 'from-blue-400 to-purple-500' },
    { label: 'Je refuse de répondre', emoji: '🤐', color: 'from-gray-400 to-slate-500' },
  ]

  const handleAnswer = (answer: string) => {
    playSound('dab')
    setSelectedAnswer(answer)
    onEasterEgg()

    setTimeout(() => {
      onAnswer(answer)
    }, 800)
  }

  const selectedReaction = reactions[selectedAnswer as keyof typeof reactions]

  return (
    <div className="space-y-8">
      {/* Question - Premium Card */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-premium p-8 text-center border-3 border-purple-200"
      >
        <motion.p
          animate={{ y: [0, -5, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="text-4xl font-black text-gradient mb-2"
        >
          Est-ce que je suis le plus beau mec que tu connaisses ? ✨
        </motion.p>
        <p className="text-sm text-gray-500 mt-2 italic">Pas de mensonges hein 👀</p>
      </motion.div>

      {/* Options - Fancy Grid */}
      <motion.div
        className="grid grid-cols-2 gap-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ staggerChildren: 0.1 }}
      >
        {options.map((option, index) => (
          <motion.button
            key={option.label}
            initial={{ opacity: 0, scale: 0.7 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.08, y: -5 }}
            whileTap={{ scale: 0.92 }}
            onClick={() => handleAnswer(option.label)}
            className={`p-6 rounded-3xl font-bold text-lg transition-all duration-300 shadow-lg ${
              selectedAnswer === option.label
                ? `bg-gradient-to-r ${option.color} text-white shadow-2xl scale-105`
                : 'bg-white border-3 border-gray-200 text-gray-800 hover:border-purple-400 hover:shadow-2xl'
            }`}
          >
            <motion.span
              animate={selectedAnswer === option.label ? { rotate: 360 } : {}}
              transition={{ duration: 0.6 }}
              className="text-4xl block mb-2"
            >
              {option.emoji}
            </motion.span>
            {option.label}
          </motion.button>
        ))}
      </motion.div>

      {/* Reaction - Animated */}
      {selectedAnswer && selectedReaction && (
        <motion.div
          initial={{ opacity: 0, scale: 0.5, rotate: -20 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 120 }}
          className={`card-premium p-8 bg-gradient-to-br ${selectedReaction.color} text-center border-3 border-purple-300 shadow-2xl`}
        >
          <motion.p
            animate={{ scale: [1, 1.15, 1] }}
            transition={{ duration: 0.6, repeat: Infinity }}
            className="text-5xl mb-3"
          >
            {selectedReaction.emoji}
          </motion.p>
          <motion.p
            animate={{ opacity: [1, 0.7, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
            className="text-xl font-black text-gray-800"
          >
            {selectedReaction.text}
          </motion.p>
        </motion.div>
      )}
    </div>
  )
}

export default Question2
