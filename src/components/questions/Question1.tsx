import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useSound } from '../../hooks/useSound'

interface Question1Props {
  onAnswer: (answer: number) => void
  onEasterEgg: () => void
}

const Question1: React.FC<Question1Props> = ({ onAnswer, onEasterEgg }) => {
  const [selectedRating, setSelectedRating] = useState<number | null>(null)
  const [showWrong, setShowWrong] = useState(false)
  const [shakeKey, setShakeKey] = useState(0)
  const { playSound } = useSound()

  const ratings = Array.from({ length: 20 }, (_, i) => i + 1)

  const handleRatingClick = (rating: number) => {
    if (rating === 20) {
      setSelectedRating(20)
      playSound('success')
      onEasterEgg()
      setTimeout(() => onAnswer(20), 800)
    } else {
      playSound('error')
      setShakeKey(prev => prev + 1)
      setShowWrong(true)
      setTimeout(() => setShowWrong(false), 2000)
    }
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
          Sur 20, combien me notes-tu ? 😏
        </p>
      </motion.div>

      {/* Wrong answer message */}
      {showWrong && (
        <motion.div
          key={shakeKey}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0 }}
          className="card-base p-4 bg-red-50 border-red-200 text-center"
        >
          <motion.p
            animate={{ x: [0, -5, 5, -5, 0] }}
            transition={{ duration: 0.5 }}
            className="text-lg font-bold text-red-600"
          >
            Pardon ???
          </motion.p>
          <p className="text-sm text-red-500 mt-2">
            Réponse invalide. Réessaie... 👀
          </p>
        </motion.div>
      )}

      {/* Rating buttons grid */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ staggerChildren: 0.05 }}
        className="grid grid-cols-4 gap-2"
      >
        {ratings.map(rating => (
          <motion.button
            key={rating}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => handleRatingClick(rating)}
            className={`py-2 rounded-xl font-bold transition-all ${
              selectedRating === rating
                ? 'bg-gradient-to-r from-rose-500 to-pink-500 text-white'
                : rating === 20
                  ? 'bg-gradient-to-r from-rose-100 to-pink-100 text-rose-600 border-2 border-rose-300 hover:border-rose-500'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {rating}
          </motion.button>
        ))}
      </motion.div>

      {/* Success message */}
      {selectedRating === 20 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card-base p-6 bg-gradient-to-r from-rose-50 to-pink-50 text-center border-rose-200"
        >
          <motion.p
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 0.5, repeat: Infinity }}
            className="text-3xl font-black text-rose-600"
          >
            ✓ CORRECT ❤️
          </motion.p>
          <p className="text-sm text-gray-600 mt-2">Tu as bon goût 😎</p>
        </motion.div>
      )}
    </div>
  )
}

export default Question1
