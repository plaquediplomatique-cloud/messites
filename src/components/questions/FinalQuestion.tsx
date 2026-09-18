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

const ARENA_WIDTH = 320
const ARENA_HEIGHT = 180

const FinalQuestion: React.FC<FinalQuestionProps> = ({ onAnswer, onEasterEgg }) => {
  const [noButtonPosition, setNoButtonPosition] = useState({ x: 0, y: 0 })
  const [noClickCount, setNoClickCount] = useState(0)
  const [noButtonText, setNoButtonText] = useState('NON')
  const noButtonRef = useRef<HTMLButtonElement>(null)
  const arenaRef = useRef<HTMLDivElement>(null)
  const { playSound } = useSound()

  const handleYesClick = () => {
    playSound('success')
    triggerConfetti('heavy')
    onEasterEgg()
    onAnswer(true)
  }

  const handleNoHover = () => {
    playSound('fart')

    // Movement is always confined to a fixed-size arena, never to the
    // full page (which grows as messages appear below), so the button
    // can never escape the visible play area.
    const arenaWidth = arenaRef.current?.clientWidth ?? ARENA_WIDTH
    const arenaHeight = arenaRef.current?.clientHeight ?? ARENA_HEIGHT
    const maxX = arenaWidth / 2 - 70
    const maxY = arenaHeight / 2 - 40

    if (noClickCount < 2) {
      const moveX = (Math.random() - 0.5) * Math.min(80, maxX * 2)
      const moveY = (Math.random() - 0.5) * Math.min(60, maxY * 2)
      setNoButtonPosition({ x: moveX, y: moveY })
    } else {
      const moveX = (Math.random() - 0.5) * 2 * maxX
      const moveY = (Math.random() - 0.5) * 2 * maxY
      setNoButtonPosition({ x: moveX, y: moveY })
    }

    setNoClickCount(prev => prev + 1)
    if (noClickCount < noTexts.length - 1) {
      setNoButtonText(noTexts[noClickCount + 1])
    }
  }

  const noButtonScale = noClickCount <= 5 ? 1 : Math.max(0.35, 1 - (noClickCount - 5) * 0.1)

  return (
    <div className="space-y-8">
      {/* Question */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-premium p-8 text-center border-4 border-rose-300"
      >
        <motion.p
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="text-4xl sm:text-5xl font-black text-gradient"
        >
          Voulez-vous être ma copine à vie ? <span className="emoji-safe">💍</span>
        </motion.p>
      </motion.div>

      {/* Buttons arena — fixed size so the NO button can never fly off past this box */}
      <motion.div
        ref={arenaRef}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative w-full mx-auto flex items-center justify-center gap-6 card-base bg-white/40"
        style={{ maxWidth: `${ARENA_WIDTH}px`, height: `${ARENA_HEIGHT}px` }}
      >
        {/* YES button - PROMINENT */}
        <motion.button
          onClick={handleYesClick}
          whileHover={{ scale: 1.1, y: -4 }}
          whileTap={{ scale: 0.95 }}
          animate={{
            boxShadow: [
              '0 20px 40px rgba(236, 72, 153, 0.3)',
              '0 20px 45px rgba(236, 72, 153, 0.55)',
              '0 20px 40px rgba(236, 72, 153, 0.3)',
            ],
          }}
          transition={{ duration: 2, repeat: Infinity }}
          className="btn-primary-rose text-xl font-black px-8 py-5 relative z-20"
        >
          ❤️ OUI
        </motion.button>

        {/* NO button - TRICKY & GOOFY, confined to the arena above */}
        <motion.button
          ref={noButtonRef}
          onMouseEnter={handleNoHover}
          onClick={handleNoHover}
          animate={{
            x: noButtonPosition.x,
            y: noButtonPosition.y,
            scale: noButtonScale,
          }}
          transition={{
            duration: 0.25,
            type: 'spring',
            stiffness: 400,
            damping: 25,
          }}
          className="btn-ghost text-base font-black px-6 py-3 whitespace-nowrap hover:bg-red-100 relative z-10"
          style={{
            opacity: noClickCount > 8 ? 0.6 : 1,
          }}
        >
          ❌ {noButtonText}
        </motion.button>
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
