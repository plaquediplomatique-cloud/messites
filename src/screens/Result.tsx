import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Heart, Sparkles } from 'lucide-react'
import { QuizAnswers } from '../App'
import { triggerConfetti, triggerHeartConfetti } from '../utils/confetti'
import { useSound } from '../hooks/useSound'

interface ResultProps {
  answers: QuizAnswers
  onRestart: () => void
  onEasterEgg: () => void
}

const Result: React.FC<ResultProps> = ({ onRestart, onEasterEgg }) => {
  const [phase, setPhase] = useState<'celebration' | 'contract' | 'personal'>('celebration')
  const { playSound } = useSound()

  useEffect(() => {
    triggerConfetti('heavy')
    triggerHeartConfetti()
    playSound('success')

    const timer1 = setTimeout(() => setPhase('contract'), 3500)
    const timer2 = setTimeout(() => setPhase('personal'), 7000)

    return () => {
      clearTimeout(timer1)
      clearTimeout(timer2)
    }
  }, [playSound])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.2,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: 'easeOut' },
    },
  }

  if (phase === 'celebration') {
    return (
      <motion.div
        key="celebration"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="min-h-screen flex items-center justify-center px-4"
      >
        <div className="text-center">
          <motion.div
            animate={{ scale: [0.5, 1.2, 1], rotate: [0, 360, 360] }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
            className="inline-block mb-8"
          >
            <Heart className="w-32 h-32 text-rose-500 fill-current" />
          </motion.div>

          <motion.h1
            animate={{ scale: [0.8, 1.1, 1] }}
            transition={{ duration: 1 }}
            className="text-6xl md:text-7xl font-black text-gradient mb-4"
          >
            JE LE SAVAIS <span className="emoji-safe">❤️</span>
          </motion.h1>

          <motion.p
            animate={{ opacity: [0, 1] }}
            transition={{ duration: 1, delay: 1 }}
            className="text-xl text-gray-700 font-semibold"
          >
            ✨ Félicitations ✨
          </motion.p>
        </div>
      </motion.div>
    )
  }

  if (phase === 'contract') {
    const today = new Date().toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
    const refNumber = `N° ${new Date().getFullYear()}-LOVE-∞`

    const articles = [
      {
        title: 'Article 1 — Durée',
        body: "Le présent contrat est conclu pour une durée indéterminée, soit jusqu'à la fin des temps, sans possibilité de préavis.",
      },
      {
        title: 'Article 2 — Résiliation',
        body: "Toute tentative de résiliation, de quelque nature que ce soit, sera automatiquement et unilatéralement rejetée par la Partie 2.",
      },
      {
        title: 'Article 3 — Support technique',
        body: 'Un support technique est assuré 24h/24 et 7j/7 par la Partie 2, sans surcoût, câlins compris.',
      },
      {
        title: 'Article 4 — Livraison de bisous',
        body: 'La Partie 2 s\'engage à livrer une quantité illimitée de bisous, sur simple demande verbale ou regard insistant.',
      },
      {
        title: 'Article 5 — Règlement des différends',
        body: "Tout différend entre les parties sera réglé à l'amiable, de préférence autour d'une pizza.",
      },
      {
        title: 'Article 6 — Clause de fierté',
        body: 'La Partie 2 se réserve le droit de dire "je le savais" à volonté, sans justification requise.',
      },
    ]

    return (
      <motion.div
        key="contract"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="min-h-screen flex items-center justify-center px-4 py-10"
      >
        <motion.div
          variants={itemVariants}
          className="contract-paper relative w-full max-w-2xl p-6 sm:p-12 rounded-sm overflow-hidden"
        >
          {/* Official stamp */}
          <motion.div
            initial={{ opacity: 0, scale: 1.6, rotate: 8 }}
            animate={{ opacity: 0.85, scale: 1, rotate: -12 }}
            transition={{ delay: 0.6, duration: 0.5, ease: 'easeOut' }}
            className="contract-stamp absolute top-20 sm:top-24 right-4 sm:right-10 px-4 py-2 text-sm sm:text-base font-black tracking-widest uppercase pointer-events-none select-none"
          >
            Approuvé ❤️
          </motion.div>

          {/* Letterhead */}
          <div className="text-center border-b-2 border-rose-800/20 pb-6 mb-6">
            <p className="uppercase tracking-[0.3em] text-[10px] sm:text-xs text-rose-800/60 font-bold mb-2">
              Tribunal Suprême de l'Amour
            </p>
            <h2 className="text-2xl sm:text-4xl font-black text-gray-900 leading-tight">
              Contrat d'Engagement Amoureux
            </h2>
            <p className="text-xs sm:text-sm text-gray-500 mt-2 italic">{refNumber}</p>
          </div>

          {/* Preamble */}
          <p className="text-gray-700 text-sm sm:text-base leading-relaxed mb-6 text-justify">
            Entre les soussignés, ci-après désignés « la Partie 1 » (Toi) et « la Partie 2 » (Moi),
            il a été établi et convenu ce qui suit, en pleine conscience et sans contrainte
            (si ce n'est celle de l'amour) :
          </p>

          {/* Articles */}
          <div className="space-y-4 mb-8">
            {articles.map((article, index) => (
              <motion.div
                key={article.title}
                variants={itemVariants}
                custom={index}
              >
                <h3 className="font-bold text-gray-900 text-sm sm:text-base mb-1">
                  {article.title}
                </h3>
                <p className="text-gray-600 text-xs sm:text-sm leading-relaxed pl-4 border-l-2 border-rose-200">
                  {article.body}
                </p>
              </motion.div>
            ))}
          </div>

          {/* Signatures */}
          <motion.div
            variants={itemVariants}
            className="grid grid-cols-2 gap-6 sm:gap-10 pt-6 border-t-2 border-rose-800/20"
          >
            <div className="text-center">
              <p className="contract-signature text-3xl sm:text-4xl text-rose-700 mb-1">
                Toi 💕
              </p>
              <div className="border-t border-gray-400 pt-1">
                <p className="text-[10px] sm:text-xs text-gray-500 uppercase tracking-wide">
                  Partie 1
                </p>
              </div>
            </div>
            <div className="text-center">
              <p className="contract-signature text-3xl sm:text-4xl text-rose-700 mb-1">
                Moi ❤️
              </p>
              <div className="border-t border-gray-400 pt-1">
                <p className="text-[10px] sm:text-xs text-gray-500 uppercase tracking-wide">
                  Partie 2
                </p>
              </div>
            </div>
          </motion.div>

          {/* Footer */}
          <motion.p
            variants={itemVariants}
            className="text-center text-[10px] sm:text-xs text-gray-400 mt-8 italic"
          >
            Signé électroniquement le {today} · Document non contraignant juridiquement,
            mais absolument contraignant émotionnellement.
          </motion.p>
        </motion.div>
      </motion.div>
    )
  }

  return (
    <motion.div
      key="personal"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="min-h-screen flex items-center justify-center px-4 py-8"
    >
      <div className="w-full max-w-2xl space-y-8">
        {/* Main message */}
        <motion.div variants={itemVariants} className="card-base p-8 text-center">
          <motion.div
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="mb-6"
          >
            <Sparkles className="w-12 h-12 text-rose-500 mx-auto" />
          </motion.div>

          <h2 className="text-3xl font-bold text-gray-800 mb-4">
            Un message sincère... 💕
          </h2>

          <motion.div
            variants={itemVariants}
            className="space-y-4 text-gray-700 leading-relaxed"
          >
            <p>
              Au-delà de tout ce goofy et cet humour absurde, tu dois savoir que tu es vraiment
              importante pour moi.
            </p>

            <p>
              Merci d'être toi. Merci de rire avec moi, même quand je fais des choses ridicules.
              Merci de rendre mes jours meilleurs juste en étant là.
            </p>

            <p>
              C'est facile de faire des blagues sur notre relation, mais la vérité, c'est que
              tu es ma personne préférée. Et je ne veux pas juste être ta copine pour la vie —
              je veux la vivre entièrement avec toi.
            </p>

            <p className="text-rose-600 font-bold text-lg pt-4">
              Je t'aime. Pour de vrai. 💗
            </p>
          </motion.div>
        </motion.div>

        {/* Buttons */}
        <motion.div variants={itemVariants} className="flex gap-4">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => triggerConfetti('medium')}
            className="flex-1 btn-primary-rose"
          >
            Encore des confettis 🎉
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onRestart}
            className="btn-ghost"
          >
            Recommencer
          </motion.button>
        </motion.div>

        {/* Easter egg hint */}
        <motion.div variants={itemVariants} className="text-center">
          <button
            onClick={onEasterEgg}
            className="text-3xl cursor-pointer hover:scale-125 transition-transform"
            title="Easter egg"
          >
            🎪
          </button>
        </motion.div>
      </div>
    </motion.div>
  )
}

export default Result
