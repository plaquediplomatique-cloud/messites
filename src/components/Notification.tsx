import React from 'react'
import { motion } from 'framer-motion'

export interface NotificationProps {
  message: string
  emoji: string
  type: 'error' | 'info' | 'success' | 'goofy'
  duration?: number
  onClose: () => void
}

const Notification: React.FC<NotificationProps> = ({
  message,
  emoji,
  type,
  duration = 2000,
  onClose,
}) => {
  React.useEffect(() => {
    const timer = setTimeout(onClose, duration)
    return () => clearTimeout(timer)
  }, [duration, onClose])

  const bgColor = {
    error: 'from-red-100 to-red-50 border-red-200',
    info: 'from-blue-100 to-blue-50 border-blue-200',
    success: 'from-green-100 to-green-50 border-green-200',
    goofy: 'from-purple-100 via-pink-100 to-yellow-50 border-purple-200',
  }[type]

  const textColor = {
    error: 'text-red-700',
    info: 'text-blue-700',
    success: 'text-green-700',
    goofy: 'text-purple-700',
  }[type]

  return (
    <motion.div
      initial={{ opacity: 0, y: -50, scale: 0.8 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -50, scale: 0.8 }}
      className={`fixed top-8 left-1/2 transform -translate-x-1/2 z-50 max-w-xs`}
    >
      <motion.div
        animate={type === 'error' ? { x: [0, -5, 5, -5, 0] } : {}}
        transition={{ duration: 0.3 }}
        className={`bg-gradient-to-r ${bgColor} border-2 rounded-2xl p-4 shadow-2xl backdrop-blur-sm`}
      >
        <div className="flex items-center gap-3">
          <motion.span
            animate={{ rotate: type === 'goofy' ? [0, -5, 5, 0] : 0 }}
            transition={{ duration: 0.5, repeat: Infinity }}
            className="text-3xl"
          >
            {emoji}
          </motion.span>
          <p className={`font-bold ${textColor} text-sm leading-snug`}>
            {message}
          </p>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default Notification
