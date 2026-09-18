import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { useSound } from '../../hooks/useSound'
import { triggerConfetti } from '../../utils/confetti'

interface FinalQuestionProps {
  onAnswer: (answer: boolean) => void
  onEasterEgg: () => void
}

const FinalQuestion: React.FC<FinalQuestionProps> = ({ onAnswer, onEasterEgg }) => {
  const [noButtonPosition, setNoButtonPosition] = useState({ x: 0, y: 0 })
  const [noClickCount, setNoClickCount] = useState(0)
  const [noButtonText, setNoButtonText] = useState('NON')
  const noButtonRef = useRef<HTMLButtonElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const { playSound } = useSound()

  const noTexts = ['NON', 'Vraiment ?', 'T\'es sûre ?', 'Réfléchis bien...', '😐', 'Bro...', 'Arrête', 'clique sur oui stp 😭']

  const handleYesClick = () => {
    playSound('success')
    triggerConfetti('heavy')
    onEasterEgg()
    onAnswer(true)
  }

  const handleNoHover = () => {
    if (noClickCount < 3) {
      const moveX = (Math.random() - 0.5) * 80
      const moveY = (Math.random() - 0.5) * 60
      setNoButtonPosition({ x: moveX, y: moveY })
    } else if (noClickCount < 6) {
      const angle = (Math.random() * Math.PI * 2)
      const distance = 100 + Math.random() * 100
      setNoButtonPosition({
        x: Math.cos(angle) * distance,
        y: Math.sin(angle) * distance
      })
    } else {
      // Random position across the screen
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect()
        const randomX = Math.random() * (rect.width - 100)
        const randomY = Math.random() * (rect.height - 100)
        setNoButtonPosition({
          x: randomX - rect.width / 2,
          y: randomY - rect.height / 2
        })
      }
    }

    setNoClickCount(prev => prev + 1)

    if (noClickCount < noTexts.length - 1) {
      setNoButtonText(noTexts[noClickCount + 1])
    }

    playSound('click')
  }

  return (
    <div ref={containerRef} className="space-y-6">
      {/* Question */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-base p-6 text-center"
      >
        <p className="text-3xl font-black text-gray-800">
          Voulez-vous être ma copine à vie ? 💍
        </p>
      </motion.div>

      {/* Buttons container */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative h-64 flex items-center justify-center gap-4"
      >
        {/* YES button */}
        <motion.button
          onClick={handleYesClick}
          whileHover={{ scale: 1.1, y: -5 }}
          whileTap={{ scale: 0.95 }}
          className="btn-primary-rose text-lg font-bold px-8 py-4 absolute left-1/2 transform -translate-x-1/2"
          style={{ top: '50%', transform: 'translate(-50%, -50%)' }}
        >
          ❤️ OUI
        </motion.button>

        {/* NO button - TRICKY */}
        <motion.button
          ref={noButtonRef}
          onMouseEnter={handleNoHover}
          onClick={handleNoHover}
          animate={{
            x: noButtonPosition.x,
            y: noButtonPosition.y,
            scale: noClickCount > 5 ? Math.max(0.3, 1 - (noClickCount - 5) * 0.1) : 1,
          }}
          transition={{
            duration: 0.3,
            type: 'spring',
            stiffness: 300,
            damping: 20
          }}
          className="btn-ghost absolute right-1/2 transform translate-x-1/2 text-lg font-bold px-6 py-3 whitespace-nowrap"
          style={{ bottom: '50%', transform: 'translate(50%, 50%)' }}
        >
          ❌ {noButtonText}
        </motion.button>
      </motion.div>

      {/* Messages based on click count */}
      {noClickCount > 2 && noClickCount < 5 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card-base p-4 bg-yellow-50 border-yellow-200 text-center"
        >
          <p className="text-yellow-700 font-semibold">
            ⚠️ Le bouton NON essaie de s\'échapper...
          </p>
        </motion.div>
      )}

      {noClickCount > 4 && noClickCount < 7 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card-base p-4 bg-red-50 border-red-200 text-center"
        >
          <motion.p
            animate={{ opacity: [1, 0.5, 1] }}
            transition={{ duration: 0.5, repeat: Infinity }}
            className="text-red-600 font-bold text-sm"
          >
            🚨 Connexion perdue avec le bouton NON
          </motion.p>
        </motion.div>
      )}

      {noClickCount >= 7 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card-base p-4 bg-gradient-to-r from-purple-50 to-pink-50 text-center"
        >
          <p className="text-gray-700 font-semibold text-sm">
            Le système a décidé pour toi 💕
          </p>
        </motion.div>
      )}

      {/* Footer hint */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="text-center text-xs text-gray-400"
      >
        {noClickCount === 0 && 'Essaie de cliquer sur NON 👀'}
        {noClickCount > 0 && 'Le destin est scellé ✨'}
      </motion.p>
    </div>
  )
}

export default FinalQuestion
