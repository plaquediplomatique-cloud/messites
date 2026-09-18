import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useSound } from '../../hooks/useSound'

interface Question3Props {
  onAnswer: (answer: string) => void
  onEasterEgg: () => void
}

const reactions = {
  Moi: { text: "Au moins t'es honnête 😂", emoji: '🤡', sound: 'fart' },
  Toi: { text: 'Les femmes sages... 👑', emoji: '👸', sound: 'dab' },
  'Ça dépend': { text: 'Réponse de sage 🧠', emoji: '🤓', sound: 'ding' },
  'Le gouvernement': { text: 'QUOI?????? 💀', emoji: '🤪', sound: 'bruh' },
}

const Question3: React.FC<Question3Props> = ({ onAnswer, onEasterEgg }) => {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [showReaction, setShowReaction] = useState(false)
  const { playSound } = useSound()

  const options = Object.keys(reactions)

  const handleAnswer = (answer: string) => {
    const reaction = reactions[answer as keyof typeof reactions]
    playSound(reaction.sound as any)
    setSelectedAnswer(answer)
    setShowReaction(true)
    onEasterEgg()

    setTimeout(() => {
      onAnswer(answer)
    }, 1500)
  }

  const selectedReaction = selectedAnswer ? reactions[selectedAnswer as keyof typeof reactions] : null

  return (
    <div className="space-y-8">
      {/* Question */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-premium p-8 text-center border-3 border-orange-200"
      >
        <motion.p
          animate={{ rotate: [0, -2, 2, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="text-4xl font-black text-gradient mb-2"
        >
          Qui a raison dans une dispute ? ⚔️
        </motion.p>
        <p className="text-sm text-gray-500 mt-2 italic">Réponds honnêtement... (ou pas 😏)</p>
      </motion.div>

      {/* Options */}
      <motion.div
        className="space-y-3"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ staggerChildren: 0.1 }}
      >
        {options.map((option, index) => {
          const isSelected = selectedAnswer === option
          return (
            <motion.button
              key={option}
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.05, x: 10 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleAnswer(option)}
              className={`w-full p-5 rounded-2xl font-bold text-lg transition-all ${
                isSelected
                  ? 'bg-gradient-to-r from-orange-500 to-yellow-500 text-white shadow-2xl scale-105'
                  : 'bg-white border-3 border-gray-300 text-gray-800 hover:border-orange-400 hover:shadow-xl shadow-md'
              }`}
            >
              <motion.span
                animate={isSelected ? { rotate: 360 } : {}}
                transition={{ duration: 0.5 }}
                className="inline-block mr-3"
              >
                {option === 'Moi' && '🤴'}
                {option === 'Toi' && '👑'}
                {option === 'Ça dépend' && '🤔'}
                {option === 'Le gouvernement' && '🏛️'}
              </motion.span>
              {option}
            </motion.button>
          )
        })}
      </motion.div>

      {/* Reaction */}
      {showReaction && selectedReaction && (
        <motion.div
          initial={{ opacity: 0, scale: 0.3, rotate: -45 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 150 }}
          className="card-premium p-8 bg-gradient-to-br from-yellow-100 via-orange-100 to-red-100 text-center border-3 border-orange-400 shadow-2xl"
        >
          <motion.p
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 0.5, repeat: Infinity }}
            className="text-5xl mb-3"
          >
            {selectedReaction.emoji}
          </motion.p>
          <motion.p
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 0.8, repeat: Infinity }}
            className="text-2xl font-black text-gray-800"
          >
            {selectedReaction.text}
          </motion.p>
        </motion.div>
      )}
    </div>
  )
}

export default Question3
