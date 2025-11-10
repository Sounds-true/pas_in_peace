/**
 * Letter Manager Page - Write letters to your child
 *
 * Protected route - requires authentication
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Save,
  Send,
  ArrowLeft,
  Eye,
  Heart,
  Sparkles,
  Image as ImageIcon,
  Smile,
  Wand2,
} from 'lucide-react';
import { useRouter } from 'next/router';
import { ProtectedRoute } from '../../components/Auth/ProtectedRoute';
import { DashboardLayout } from '../../components/Dashboard';

type LetterType = 'gratitude' | 'apology' | 'memory' | 'hope';

interface LetterData {
  type: LetterType;
  title: string;
  content: string;
  recipient: string;
  isPrivate: boolean;
}

function LetterWriterContent() {
  const router = useRouter();
  const [selectedType, setSelectedType] = useState<LetterType | null>(null);
  const [letterData, setLetterData] = useState<LetterData>({
    type: 'gratitude',
    title: '',
    content: '',
    recipient: '',
    isPrivate: true,
  });
  const [isAiAssisting, setIsAiAssisting] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const letterTypes = [
    {
      type: 'gratitude' as LetterType,
      emoji: '🙏',
      title: 'Благодарность',
      description: 'Выразите благодарность за моменты вместе',
      color: 'blue',
      template:
        'Дорогой/Дорогая [Имя],\n\nЯ хочу сказать тебе спасибо за...\n\nС любовью,\n[Твоё имя]',
    },
    {
      type: 'apology' as LetterType,
      emoji: '💙',
      title: 'Извинение',
      description: 'Искренне попросите прощения',
      color: 'purple',
      template:
        'Дорогой/Дорогая [Имя],\n\nМне очень жаль, что...\n\nЯ хочу, чтобы ты знал/знала, что...\n\nС любовью,\n[Твоё имя]',
    },
    {
      type: 'memory' as LetterType,
      emoji: '📸',
      title: 'Воспоминание',
      description: 'Поделитесь особенным воспоминанием',
      color: 'pink',
      template:
        'Дорогой/Дорогая [Имя],\n\nПомню тот раз, когда мы...\n\nЭто было так здорово, потому что...\n\nС любовью,\n[Твоё имя]',
    },
    {
      type: 'hope' as LetterType,
      emoji: '✨',
      title: 'Надежда',
      description: 'Выразите надежду на будущее',
      color: 'cyan',
      template:
        'Дорогой/Дорогая [Имя],\n\nЯ мечтаю о том дне, когда...\n\nЯ верю, что мы...\n\nС любовью,\n[Твоё имя]',
    },
  ];

  const handleSelectType = (type: LetterType) => {
    setSelectedType(type);
    const selectedTemplate =
      letterTypes.find((t) => t.type === type)?.template || '';
    setLetterData({
      ...letterData,
      type,
      content: selectedTemplate,
    });
  };

  const handleAiAssist = async () => {
    setIsAiAssisting(true);
    // Simulate AI assistance
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Generate AI suggestion based on type
    let suggestion = '';
    switch (letterData.type) {
      case 'gratitude':
        suggestion =
          '\n\n💡 Подсказка от AI:\nПопробуйте вспомнить конкретный момент, который сделал вас счастливым. Например: "Помню, как ты улыбался, когда мы вместе..." Конкретные детали делают благодарность более искренней.';
        break;
      case 'apology':
        suggestion =
          '\n\n💡 Подсказка от AI:\nВажно признать свои чувства и показать понимание последствий. Попробуйте: "Я понимаю, что мои действия могли задеть тебя, и мне очень жаль..."';
        break;
      case 'memory':
        suggestion =
          '\n\n💡 Подсказка от AI:\nОпишите момент через органы чувств - что вы видели, слышали, чувствовали. Это сделает воспоминание живым: "Я помню запах моря и твой смех..."';
        break;
      case 'hope':
        suggestion =
          '\n\n💡 Подсказка от AI:\nПоделитесь конкретной мечтой о будущем: "Я представляю, как мы вместе..." Это даёт ребёнку позитивное видение.';
        break;
    }

    setLetterData({
      ...letterData,
      content: letterData.content + suggestion,
    });
    setIsAiAssisting(false);
  };

  const handleSave = () => {
    // TODO: Save to backend
    router.push('/projects');
  };

  if (!selectedType) {
    return (
      <DashboardLayout
        title="Написать письмо"
        actions={
          <button
            onClick={() => router.push('/dashboard')}
            className="glass-button bg-white/10 hover:bg-white/20 flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Назад
          </button>
        }
      >
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <motion.div
            className="text-center mb-12"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="text-6xl mb-4">💌</div>
            <h2 className="text-3xl font-bold text-white mb-2">
              Выберите тип письма
            </h2>
            <p className="text-white/70">
              AI-ассистент поможет вам найти правильные слова
            </p>
          </motion.div>

          {/* Letter type selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {letterTypes.map((type, index) => (
              <motion.button
                key={type.type}
                onClick={() => handleSelectType(type.type)}
                className="frosted-card text-left hover:scale-105 transition-all group"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -4 }}
              >
                <div className="text-5xl mb-4">{type.emoji}</div>
                <h3 className="text-2xl font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">
                  {type.title}
                </h3>
                <p className="text-white/70 mb-6">{type.description}</p>
                <div
                  className={`
                  flex items-center gap-2 text-sm font-medium
                  ${type.color === 'blue' && 'text-blue-400'}
                  ${type.color === 'purple' && 'text-purple-400'}
                  ${type.color === 'pink' && 'text-pink-400'}
                  ${type.color === 'cyan' && 'text-cyan-400'}
                `}
                >
                  <span>Выбрать</span>
                  <Sparkles className="w-4 h-4" />
                </div>
              </motion.button>
            ))}
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const currentType = letterTypes.find((t) => t.type === selectedType);

  return (
    <DashboardLayout
      title={`Письмо: ${currentType?.title}`}
      actions={
        <div className="flex gap-2">
          <button
            onClick={() => setShowPreview(!showPreview)}
            className="glass-button bg-purple-500/20 hover:bg-purple-500/30 flex items-center gap-2"
          >
            <Eye className="w-4 h-4" />
            {showPreview ? 'Редактор' : 'Превью'}
          </button>
          <button
            onClick={handleSave}
            className="glass-button bg-blue-500/20 hover:bg-blue-500/30 flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            Сохранить
          </button>
        </div>
      }
    >
      <div className="max-w-4xl mx-auto">
        {/* Type indicator */}
        <motion.div
          className="frosted-card mb-6 flex items-center gap-4"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="text-4xl">{currentType?.emoji}</div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-white">{currentType?.title}</h3>
            <p className="text-sm text-white/70">{currentType?.description}</p>
          </div>
          <button
            onClick={() => setSelectedType(null)}
            className="glass-button bg-white/10 hover:bg-white/20 text-sm"
          >
            Изменить тип
          </button>
        </motion.div>

        {!showPreview ? (
          /* Editor mode */
          <motion.div
            className="frosted-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {/* Title */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-white/70 mb-2">
                Заголовок письма (необязательно)
              </label>
              <input
                type="text"
                value={letterData.title}
                onChange={(e) =>
                  setLetterData({ ...letterData, title: e.target.value })
                }
                placeholder="Например: Моя благодарность"
                className="w-full bg-white/5 rounded-xl px-4 py-3 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50"
              />
            </div>

            {/* Recipient */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-white/70 mb-2">
                Кому (имя ребёнка)
              </label>
              <input
                type="text"
                value={letterData.recipient}
                onChange={(e) =>
                  setLetterData({ ...letterData, recipient: e.target.value })
                }
                placeholder="Имя"
                className="w-full bg-white/5 rounded-xl px-4 py-3 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50"
              />
            </div>

            {/* Editor toolbar */}
            <div className="flex items-center gap-2 mb-4 pb-4 border-b border-white/10">
              <button
                onClick={handleAiAssist}
                disabled={isAiAssisting}
                className="glass-button bg-purple-500/20 hover:bg-purple-500/30 flex items-center gap-2 text-sm disabled:opacity-50"
              >
                {isAiAssisting ? (
                  <>
                    <Wand2 className="w-4 h-4 animate-pulse" />
                    Думаю...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-4 h-4" />
                    AI подсказка
                  </>
                )}
              </button>
              <button
                disabled
                className="glass-button bg-white/10 hover:bg-white/20 p-2 opacity-50"
                title="Coming soon"
              >
                <ImageIcon className="w-4 h-4" />
              </button>
              <button
                disabled
                className="glass-button bg-white/10 hover:bg-white/20 p-2 opacity-50"
                title="Coming soon"
              >
                <Smile className="w-4 h-4" />
              </button>
            </div>

            {/* Content editor */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-white/70 mb-2">
                Текст письма
              </label>
              <textarea
                value={letterData.content}
                onChange={(e) =>
                  setLetterData({ ...letterData, content: e.target.value })
                }
                rows={15}
                className="w-full bg-white/5 rounded-xl px-4 py-3 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50 resize-none font-serif leading-relaxed"
              />
              <p className="text-xs text-white/50 mt-2">
                {letterData.content.length} символов
              </p>
            </div>

            {/* Privacy settings */}
            <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
              <div>
                <h4 className="text-white font-medium flex items-center gap-2">
                  <Heart className="w-4 h-4 text-pink-400" />
                  Приватное письмо
                </h4>
                <p className="text-sm text-white/60">
                  Только вы можете видеть это письмо
                </p>
              </div>
              <button
                onClick={() =>
                  setLetterData({
                    ...letterData,
                    isPrivate: !letterData.isPrivate,
                  })
                }
                className={`
                  relative w-12 h-6 rounded-full transition-colors
                  ${letterData.isPrivate ? 'bg-pink-500' : 'bg-white/20'}
                `}
              >
                <motion.div
                  className="absolute top-1 w-4 h-4 rounded-full bg-white"
                  animate={{
                    left: letterData.isPrivate ? '28px' : '4px',
                  }}
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                />
              </button>
            </div>
          </motion.div>
        ) : (
          /* Preview mode */
          <motion.div
            className="frosted-card"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <div className="max-w-2xl mx-auto">
              {/* Letter preview */}
              <div className="bg-white/5 rounded-2xl p-8 md:p-12 shadow-2xl">
                {letterData.title && (
                  <h2 className="text-2xl font-bold text-white mb-6 text-center border-b border-white/20 pb-4">
                    {letterData.title}
                  </h2>
                )}
                <div className="prose prose-invert max-w-none">
                  <div className="text-white/90 whitespace-pre-wrap font-serif text-lg leading-relaxed">
                    {letterData.content}
                  </div>
                </div>
                {letterData.recipient && (
                  <div className="mt-8 pt-6 border-t border-white/20">
                    <p className="text-white/70 text-sm">
                      Для: <span className="text-white font-medium">{letterData.recipient}</span>
                    </p>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="mt-6 flex gap-3">
                <button
                  onClick={handleSave}
                  className="flex-1 glass-button bg-blue-500/20 hover:bg-blue-500/30 flex items-center justify-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  Сохранить письмо
                </button>
                <button
                  disabled
                  className="glass-button bg-green-500/20 hover:bg-green-500/30 flex items-center gap-2 opacity-50 cursor-not-allowed"
                  title="Coming soon"
                >
                  <Send className="w-4 h-4" />
                  Отправить
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </DashboardLayout>
  );
}

export default function LetterWriterPage() {
  return (
    <ProtectedRoute>
      <LetterWriterContent />
    </ProtectedRoute>
  );
}
