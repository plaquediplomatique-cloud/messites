import React, { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { useSound } from '../../hooks/useSound'
import { triggerConfetti } from '../../utils/confetti'

interface FinalQuestionProps {
  onAnswer: (answer: boolean) => void
  onEasterEgg: () => void
}

const noTexts = [
  'NON',
  'Vraiment ?',
  "T'es sûre ?",
  'Réfléchis bien...',
  '😐',
  'Bro...',
  'Arrête',
  'clique sur oui stp 😭',
  'NAH FAH',
  'Ça pue',
  'Non sérieux',
  '💀',
  'Je vais mourir',
]

const FinalQuestion: React.FC<FinalQuestionProps> = ({ onAnswer, onEasterEgg }) => {
  const [noButtonPosition, setNoButtonPosition] = useState({ x: 0, y: 0 })
  const [noClickCount, setNoClickCount] = useState(0)
  const [noButtonText, setNoButtonText] = useState('NON')
  const noButtonRef = useRef<HTMLButtonElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const { playSound } = useSound()

  const handleYesClick = () => {
    playSound('success')
    triggerConfetti('heavy')
    onEasterEgg()
    onAnswer(true)
  }

  const handleNoHover = () => {
    playSound('fart')

    if (noClickCount < 2) {
      const moveX = (Math.random() - 0.5) * 60
      const moveY = (Math.random() - 0.5) * 40
      setNoButtonPosition({ x: moveX, y: moveY })
    } else if (noClickCount < 5) {
      const angle = Math.random() * Math.PI * 2
      const distance = 80 + Math.random() * 120
      setNoButtonPosition({
        x: Math.cos(angle) * distance,
        y: Math.sin(angle) * distance,
      })
    } else {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect()
        const randomX = Math.random() * (rect.width - 80)
        const randomY = Math.random() * (rect.height - 80)
        setNoButtonPosition({
          x: randomX - rect.width / 2,
          y: randomY - rect.height / 2,
        })
      }
    }

    setNoClickCount(prev => prev + 1)
    if (noClickCount < noTexts.length - 1) {
      setNoButtonText(noTexts[noClickCount + 1])
    }
  }

  return (
    <div ref={containerRef} className="space-y-8">
      {/* Question */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-premium p-8 text-center border-4 border-rose-300"
      >
        <motion.p
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="text-5xl font-black text-gradient"
        >
          Voulez-vous être ma copine à vie ? 💍
        </motion.p>
      </motion.div>

      {/* Buttons container */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex items-center justify-center gap-6 p-8 relative"
        style={{ minHeight: '200px' }}
      >
        {/* YES button - PROMINENT */}
        <motion.button
          onClick={handleYesClick}
          whileHover={{ scale: 1.15, y: -8 }}
          whileTap={{ scale: 0.95 }}
          animate={{ y: [0, -5, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="btn-primary-rose text-2xl font-black px-10 py-6 shadow-2xl relative z-20"
        >
          ❤️ OUI
        </motion.button>

        {/* NO button - TRICKY & GOOFY */}
        <motion.div
          className="relative"
          style={{ width: '120px', height: '60px' }}
        >
          <motion.button
            ref={noButtonRef}
            onMouseEnter={handleNoHover}
            onClick={handleNoHover}
            animate={{
              x: noButtonPosition.x,
              y: noButtonPosition.y,
              scale: Math.max(0.2, 1 - (noClickCount - 5) * 0.12),
            }}
            transition={{
              duration: 0.25,
              type: 'spring',
              stiffness: 400,
              damping: 25,
            }}
            className="btn-ghost text-lg font-black px-8 py-4 whitespace-nowrap hover:bg-red-100 absolute left-0 top-0"
            style={{
              opacity: noClickCount > 8 ? 0.6 : 1,
            }}
          >
            ❌ {noButtonText}
          </motion.button>
        </motion.div>
      </motion.div>

      {/* Messages based on click count */}
      {noClickCount > 0 && noClickCount < 3 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          key={`msg-${noClickCount}`}
          className="card-premium p-4 bg-yellow-100 border-yellow-300 text-center border-3"
        >
          <motion.p className="text-yellow-800 font-black text-lg">
            ⚠️ Le bouton NON essaie de s'échapper...
          </motion.p>
        </motion.div>
      )}

      {noClickCount > 2 && noClickCount < 6 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          key={`msg-${noClickCount}`}
          className="card-premium p-4 bg-red-100 border-red-300 text-center border-3"
        >
          <motion.p
            animate={{ opacity: [1, 0.4, 1] }}
            transition={{ duration: 0.6, repeat: Infinity }}
            className="text-red-800 font-black text-lg"
          >
            🚨 Connexion perdue avec le bouton NON 🚨
          </motion.p>
        </motion.div>
      )}

      {noClickCount > 5 && noClickCount < 10 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          key={`msg-${noClickCount}`}
          className="card-premium p-4 bg-purple-100 border-purple-300 text-center border-3"
        >
          <motion.p className="text-purple-800 font-black text-lg">
            💜 Le système a pris une décision pour toi...
          </motion.p>
        </motion.div>
      )}

      {noClickCount >= 10 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          key={`msg-${noClickCount}`}
          className="card-premium p-6 bg-gradient-to-r from-pink-200 to-rose-200 text-center border-4 border-rose-400"
        >
          <motion.p
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 0.8, repeat: Infinity }}
            className="text-2xl font-black text-gray-800"
          >
            C'est signé, c'est officiel maintenant 🔐
          </motion.p>
        </motion.div>
      )}

      {/* Footer hint */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="text-center text-xs text-gray-500 italic"
      >
        {noClickCount === 0 && 'Essaie de cliquer sur NON... 👀'}
        {noClickCount > 0 && noClickCount < 5 && 'Ça va être dur... 😏'}
        {noClickCount >= 5 && 'Le destin est scellé ✨'}
      </motion.p>
    </div>
  )
}

export default FinalQuestion
