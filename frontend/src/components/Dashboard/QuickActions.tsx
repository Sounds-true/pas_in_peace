/**
 * QuickActions - Quick action buttons with modals
 *
 * Features:
 * - Create Quest modal
 * - Write Letter modal
 * - Set Goal modal
 * - Glass morphism design
 * - Smooth animations
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, Mail, Target, ArrowRight } from 'lucide-react';
import { useRouter } from 'next/router';

export interface QuickActionsProps {
  className?: string;
}

type ModalType = 'quest' | 'letter' | 'goal' | null;

export const QuickActions: React.FC<QuickActionsProps> = ({ className = '' }) => {
  const [activeModal, setActiveModal] = useState<ModalType>(null);
  const router = useRouter();

  const openModal = (type: ModalType) => setActiveModal(type);
  const closeModal = () => setActiveModal(null);

  return (
    <>
      {/* Action buttons */}
      <div className={`grid grid-cols-1 md:grid-cols-3 gap-6 ${className}`}>
        {/* Create Quest */}
        <motion.button
          onClick={() => openModal('quest')}
          className="frosted-card hover:scale-105 transition-transform text-left group"
          whileHover={{ y: -4 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="flex items-start justify-between mb-4">
            <div className="text-5xl">✨</div>
            <Sparkles className="w-6 h-6 text-yellow-400 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <h4 className="text-xl font-bold text-white mb-2">Создать квест</h4>
          <p className="text-white/70 text-sm mb-4">
            Персонализированный образовательный квест для вашего ребёнка
          </p>
          <div className="flex items-center text-blue-400 text-sm font-medium">
            <span>Начать</span>
            <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
          </div>
        </motion.button>

        {/* Write Letter */}
        <motion.button
          onClick={() => openModal('letter')}
          className="frosted-card hover:scale-105 transition-transform text-left group"
          whileHover={{ y: -4 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="flex items-start justify-between mb-4">
            <div className="text-5xl">💌</div>
            <Mail className="w-6 h-6 text-pink-400 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <h4 className="text-xl font-bold text-white mb-2">Написать письмо</h4>
          <p className="text-white/70 text-sm mb-4">
            Выразите свои чувства через благодарность, извинение или воспоминание
          </p>
          <div className="flex items-center text-pink-400 text-sm font-medium">
            <span>Начать</span>
            <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
          </div>
        </motion.button>

        {/* Set Goal */}
        <motion.button
          onClick={() => openModal('goal')}
          className="frosted-card hover:scale-105 transition-transform text-left group"
          whileHover={{ y: -4 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="flex items-start justify-between mb-4">
            <div className="text-5xl">🎯</div>
            <Target className="w-6 h-6 text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <h4 className="text-xl font-bold text-white mb-2">Поставить цель</h4>
          <p className="text-white/70 text-sm mb-4">
            Определите следующие шаги на пути восстановления связи
          </p>
          <div className="flex items-center text-purple-400 text-sm font-medium">
            <span>Начать</span>
            <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
          </div>
        </motion.button>
      </div>

      {/* Modals */}
      <AnimatePresence>
        {activeModal && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {/* Backdrop */}
            <motion.div
              className="absolute inset-0 bg-black/70 backdrop-blur-sm"
              onClick={closeModal}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />

            {/* Modal content */}
            <motion.div
              className="relative z-10 w-full max-w-2xl"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            >
              <div className="frosted-card">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-2xl font-bold text-white">
                    {activeModal === 'quest' && '✨ Создать квест'}
                    {activeModal === 'letter' && '💌 Написать письмо'}
                    {activeModal === 'goal' && '🎯 Поставить цель'}
                  </h3>
                  <button
                    onClick={closeModal}
                    className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                  >
                    <X className="w-6 h-6 text-white/70 hover:text-white" />
                  </button>
                </div>

                {/* Content based on type */}
                {activeModal === 'quest' && (
                  <QuestModal onClose={closeModal} />
                )}
                {activeModal === 'letter' && (
                  <LetterModal onClose={closeModal} />
                )}
                {activeModal === 'goal' && (
                  <GoalModal onClose={closeModal} />
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

// Quest Modal
const QuestModal: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const router = useRouter();

  return (
    <div className="space-y-6">
      <p className="text-white/70">
        Создайте персонализированный образовательный квест для вашего ребёнка с
        помощью AI-ассистента.
      </p>

      <div className="space-y-4">
        <div className="liquid-glass-hover p-4 rounded-xl">
          <h4 className="text-white font-medium mb-2">📚 Образовательный квест</h4>
          <p className="text-white/60 text-sm">
            Квест с учётом интересов и возраста ребёнка
          </p>
        </div>

        <div className="liquid-glass-hover p-4 rounded-xl">
          <h4 className="text-white font-medium mb-2">🎮 Игровой квест</h4>
          <p className="text-white/60 text-sm">
            Развлекательный квест с элементами обучения
          </p>
        </div>

        <div className="liquid-glass-hover p-4 rounded-xl">
          <h4 className="text-white font-medium mb-2">❤️ Эмоциональный квест</h4>
          <p className="text-white/60 text-sm">
            Квест для обсуждения чувств и воспоминаний
          </p>
        </div>
      </div>

      <div className="flex gap-3 pt-4">
        <button
          onClick={() => {
            router.push('/quest-builder/new');
            onClose();
          }}
          className="glass-button flex-1 bg-blue-500/20 hover:bg-blue-500/30"
        >
          Начать создание
        </button>
        <button
          onClick={onClose}
          className="glass-button bg-white/10 hover:bg-white/20"
        >
          Отмена
        </button>
      </div>
    </div>
  );
};

// Letter Modal
const LetterModal: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const router = useRouter();

  return (
    <div className="space-y-6">
      <p className="text-white/70">
        Выберите тип письма, которое вы хотите написать вашему ребёнку.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <button className="liquid-glass-hover p-4 rounded-xl text-left hover:scale-105 transition-transform">
          <div className="text-3xl mb-2">🙏</div>
          <h4 className="text-white font-medium mb-1">Благодарность</h4>
          <p className="text-white/60 text-sm">
            Выразите благодарность за моменты вместе
          </p>
        </button>

        <button className="liquid-glass-hover p-4 rounded-xl text-left hover:scale-105 transition-transform">
          <div className="text-3xl mb-2">💙</div>
          <h4 className="text-white font-medium mb-1">Извинение</h4>
          <p className="text-white/60 text-sm">
            Искренне попросите прощения
          </p>
        </button>

        <button className="liquid-glass-hover p-4 rounded-xl text-left hover:scale-105 transition-transform">
          <div className="text-3xl mb-2">📸</div>
          <h4 className="text-white font-medium mb-1">Воспоминание</h4>
          <p className="text-white/60 text-sm">
            Поделитесь особенным воспоминанием
          </p>
        </button>

        <button className="liquid-glass-hover p-4 rounded-xl text-left hover:scale-105 transition-transform">
          <div className="text-3xl mb-2">✨</div>
          <h4 className="text-white font-medium mb-1">Надежда</h4>
          <p className="text-white/60 text-sm">
            Выразите надежду на будущее
          </p>
        </button>
      </div>

      <div className="flex gap-3 pt-4">
        <button
          onClick={() => {
            router.push('/letters/new');
            onClose();
          }}
          className="glass-button flex-1 bg-pink-500/20 hover:bg-pink-500/30"
        >
          Продолжить
        </button>
        <button
          onClick={onClose}
          className="glass-button bg-white/10 hover:bg-white/20"
        >
          Отмена
        </button>
      </div>
    </div>
  );
};

// Goal Modal
const GoalModal: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const router = useRouter();

  return (
    <div className="space-y-6">
      <p className="text-white/70">
        Поставьте цель для одного из 4 треков восстановления.
      </p>

      <div className="space-y-3">
        <button className="w-full liquid-glass-hover p-4 rounded-xl text-left flex items-center gap-4 hover:scale-105 transition-transform">
          <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center">
            <span className="text-2xl">🧘</span>
          </div>
          <div className="flex-1">
            <h4 className="text-white font-medium">Работа над собой</h4>
            <p className="text-white/60 text-sm">
              Эмоциональное благополучие и саморазвитие
            </p>
          </div>
        </button>

        <button className="w-full liquid-glass-hover p-4 rounded-xl text-left flex items-center gap-4 hover:scale-105 transition-transform">
          <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center">
            <span className="text-2xl">❤️</span>
          </div>
          <div className="flex-1">
            <h4 className="text-white font-medium">Связь с ребёнком</h4>
            <p className="text-white/60 text-sm">
              Восстановление эмоциональной связи
            </p>
          </div>
        </button>

        <button className="w-full liquid-glass-hover p-4 rounded-xl text-left flex items-center gap-4 hover:scale-105 transition-transform">
          <div className="w-12 h-12 rounded-full bg-pink-500/20 flex items-center justify-center">
            <span className="text-2xl">🤝</span>
          </div>
          <div className="flex-1">
            <h4 className="text-white font-medium">Переговоры</h4>
            <p className="text-white/60 text-sm">
              Коммуникация с другим родителем
            </p>
          </div>
        </button>

        <button className="w-full liquid-glass-hover p-4 rounded-xl text-left flex items-center gap-4 hover:scale-105 transition-transform">
          <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center">
            <span className="text-2xl">👥</span>
          </div>
          <div className="flex-1">
            <h4 className="text-white font-medium">Сообщество</h4>
            <p className="text-white/60 text-sm">
              Поддержка других родителей
            </p>
          </div>
        </button>
      </div>

      <div className="flex gap-3 pt-4">
        <button
          onClick={() => {
            router.push('/goals/new');
            onClose();
          }}
          className="glass-button flex-1 bg-purple-500/20 hover:bg-purple-500/30"
        >
          Продолжить
        </button>
        <button
          onClick={onClose}
          className="glass-button bg-white/10 hover:bg-white/20"
        >
          Отмена
        </button>
      </div>
    </div>
  );
};

export default QuickActions;
