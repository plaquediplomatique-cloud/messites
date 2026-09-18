import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useSound } from '../../hooks/useSound'

interface Question3Props {
  onAnswer: (answer: string) => void
  onEasterEgg: () => void
}

const Question3: React.FC<Question3Props> = ({ onAnswer, onEasterEgg }) => {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [showReaction, setShowReaction] = useState(false)
  const { playSound } = useSound()

  const options = [
    { label: 'Moi', emoji: '🤴' },
    { label: 'Toi', emoji: '👑' },
    { label: 'Ça dépend', emoji: '🤔' },
    { label: 'Le gouvernement', emoji: '🏛️' },
  ]

  const reactions = {
    'Moi': 'Narcissisme confirmé 😂',
    'Toi': 'Au moins tu es honnête 👏',
    'Ça dépend': 'La réponse de quelqu\'un de sage 🧠',
    'Le gouvernement': 'Bro... 💀',
  }

  const handleAnswer = (answer: string) => {
    playSound('success')
    setSelectedAnswer(answer)
    setShowReaction(true)
    onEasterEgg()

    setTimeout(() => {
      onAnswer(answer)
    }, 1500)
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
          Qui a raison dans une dispute ? ⚔️
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
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05, x: -8 }}
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

      {/* Reaction */}
      {showReaction && selectedAnswer && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8, rotate: -5 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 200 }}
          className="card-base p-4 bg-gradient-to-r from-yellow-50 to-orange-50 text-center"
        >
          <motion.p
            animate={{ y: [0, -5, 0] }}
            transition={{ duration: 1, repeat: Infinity }}
            className="text-gray-700 font-semibold"
          >
            {reactions[selectedAnswer as keyof typeof reactions]}
          </motion.p>
        </motion.div>
      )}
    </div>
  )
}

export default Question3
