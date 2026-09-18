import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useSound } from '../../hooks/useSound'
import Notification from '../Notification'

interface Question1Props {
  onAnswer: (answer: number) => void
  onEasterEgg: () => void
}

const wrongMessages = [
  { text: 'Pardon ???', emoji: '😤', sound: 'fart' },
  { text: 'NAH BRO 💀', emoji: '💀', sound: 'bruh' },
  { text: 'Ça pue la débilité', emoji: '🤢', sound: 'cringe' },
  { text: "T'es sérieux là?", emoji: '😭', sound: 'fail' },
  { text: 'Je vais crier', emoji: '😱', sound: 'dab' },
  { text: "C'était quoi ça???", emoji: '🤨', sound: 'error' },
  { text: 'Big fail 💀', emoji: '🚨', sound: 'fail' },
  { text: 'Ça me tue 😂', emoji: '⚰️', sound: 'fart' },
]

const Question1: React.FC<Question1Props> = ({ onAnswer, onEasterEgg }) => {
  const [selectedRating, setSelectedRating] = useState<number | null>(null)
  const [wrongCount, setWrongCount] = useState(0)
  const [notification, setNotification] = useState<any>(null)
  const { playSound } = useSound()

  const ratings = Array.from({ length: 20 }, (_, i) => i + 1)

  const handleRatingClick = (rating: number) => {
    if (rating === 20) {
      setSelectedRating(20)
      playSound('success')
      onEasterEgg()
      setTimeout(() => onAnswer(20), 1000)
    } else {
      const wrongMsg = wrongMessages[wrongCount % wrongMessages.length]
      playSound(wrongMsg.sound as any)
      setNotification(wrongMsg)
      setWrongCount(prev => prev + 1)
      setTimeout(() => setNotification(null), 2500)
    }
  }

  return (
    <div className="space-y-8">
      {/* Question Card */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-premium p-8 text-center border-3 border-rose-200"
      >
        <motion.p
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 1, repeat: Infinity }}
          className="text-4xl font-black text-gradient mb-2"
        >
          Sur 20, combien me notes-tu ? 😏
        </motion.p>
        <p className="text-sm text-gray-500 mt-2 italic">
          Choisis bien... je regarde 👀
        </p>
      </motion.div>

      {/* Notification */}
      <AnimatePresence>
        {notification && (
          <Notification
            message={notification.text}
            emoji={notification.emoji}
            type="goofy"
            duration={2000}
            onClose={() => setNotification(null)}
          />
        )}
      </AnimatePresence>

      {/* Rating buttons grid - Premium style */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ staggerChildren: 0.03, delayChildren: 0.1 }}
        className="grid grid-cols-5 gap-3 p-6 card-base bg-gradient-to-br from-white/50 to-rose-50/30"
      >
        {ratings.map((rating, index) => (
          <motion.button
            key={rating}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.02 }}
            whileHover={{ scale: 1.15, rotate: 2 }}
            whileTap={{ scale: 0.85 }}
            onClick={() => handleRatingClick(rating)}
            className={`py-3 rounded-xl font-bold text-sm transition-all duration-200 ${
              selectedRating === rating
                ? 'bg-gradient-to-r from-rose-500 to-pink-500 text-white shadow-xl scale-110 font-black'
                : rating === 20
                  ? 'bg-gradient-to-r from-yellow-300 to-yellow-200 text-yellow-900 border-3 border-yellow-400 shadow-lg hover:shadow-2xl font-black'
                  : 'bg-white border-2 border-gray-300 text-gray-800 hover:border-rose-400 hover:bg-rose-50 shadow-md'
            }`}
          >
            {rating}
          </motion.button>
        ))}
      </motion.div>

      {/* Success message - EXPLOSIVE */}
      {selectedRating === 20 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.3, rotate: -45 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 100, damping: 15 }}
          className="card-premium p-8 bg-gradient-to-br from-rose-200 via-pink-200 to-rose-100 text-center border-4 border-rose-500 shadow-2xl"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity }}
            className="inline-block"
          >
            ✨
          </motion.div>
          <motion.p
            animate={{
              scale: [1, 1.2, 1],
              textShadow: [
                '0 0 0px rgba(236, 72, 153, 0)',
                '0 0 20px rgba(236, 72, 153, 0.8)',
                '0 0 0px rgba(236, 72, 153, 0)',
              ],
            }}
            transition={{ duration: 0.5, repeat: Infinity }}
            className="text-5xl font-black text-rose-600 mb-2"
          >
            ✓ CORRECT ❤️
          </motion.p>
          <p className="text-lg text-rose-700 font-bold mt-2">
            T'as ENFIN bon goût 😎
          </p>
        </motion.div>
      )}

      {/* Wrong attempts counter */}
      {wrongCount > 0 && selectedRating !== 20 && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center text-xs text-gray-400 italic"
        >
          Tentatives échouées : {wrongCount}
        </motion.p>
      )}
    </div>
  )
}

export default Question1
