import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useSound } from '../../hooks/useSound'

interface Question7Props {
  onAnswer: (answer: string) => void
  onEasterEgg: () => void
}

const Question7: React.FC<Question7Props> = ({ onAnswer, onEasterEgg }) => {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const { playSound } = useSound()

  const scenarios = [
    {
      text: "...j'oublie ton anniversaire 💀",
      options: ['Très très énervé', 'Assez énervé', 'Ça va', "Je m'en fous"],
      emoji: '🎂'
    }
  ]

  const scenario = scenarios[0]

  const handleAnswer = (answer: string) => {
    if (answer === 'Très très énervé') {
      playSound('fail')
    } else if (answer === "Je m'en fous") {
      playSound('dab')
    } else {
      playSound('success')
    }
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
        <p className="text-2xl font-black text-gray-800 mb-4">
          À quel point tu serais énervée si {scenario.text}
        </p>
      </motion.div>

      {/* Emoji indicator */}
      <motion.div
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ duration: 1.5, repeat: Infinity }}
        className="text-center text-6xl"
      >
        {scenario.emoji}
      </motion.div>

      {/* Options */}
      <motion.div
        className="space-y-3"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ staggerChildren: 0.1 }}
      >
        {scenario.options.map((option, index) => (
          <motion.button
            key={option}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleAnswer(option)}
            className={`w-full p-4 rounded-2xl font-bold text-lg transition-all ${
              selectedAnswer === option
                ? 'bg-gradient-to-r from-rose-500 to-pink-500 text-white shadow-lg'
                : 'bg-white border-2 border-gray-200 text-gray-800 hover:border-rose-300 hover:bg-rose-50'
            }`}
          >
            {option}
          </motion.button>
        ))}
      </motion.div>

      {/* Response */}
      {selectedAnswer && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className={`card-base p-6 text-center border-2 ${
            selectedAnswer === 'Très très énervé'
              ? 'bg-gradient-to-br from-red-50 to-rose-50 border-red-300'
              : selectedAnswer === "Je m'en fous"
              ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-300'
              : 'bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-300'
          }`}
        >
          <motion.p
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 0.6, repeat: Infinity }}
            className="font-bold text-lg mb-2"
          >
            {selectedAnswer === 'Très très énervé' ? (
              <span className="text-red-600">😱 OK JE NOTE! JAMAIS J'OUBLIERAI!</span>
            ) : selectedAnswer === 'Assez énervé' ? (
              <span className="text-orange-600">😅 Attention noté, je vais mettre une alarme</span>
            ) : selectedAnswer === 'Ça va' ? (
              <span className="text-blue-600">😎 Cool, on peut chill sur ce sujet</span>
            ) : (
              <span className="text-green-600">💀 T'ES DÉSINVOLTE LÀ... J'AIME ÇA</span>
            )}
          </motion.p>
          <p className="text-sm text-gray-600 font-semibold">
            Réaction enregistrée ✓
          </p>
        </motion.div>
      )}
    </div>
  )
}

export default Question7
