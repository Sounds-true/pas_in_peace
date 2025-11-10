/**
 * Help Page - FAQ and support
 *
 * Protected route - requires authentication
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronDown,
  MessageCircle,
  Mail,
  Phone,
  Book,
  Video,
  ExternalLink,
  HelpCircle,
  Heart,
  Sparkles,
} from 'lucide-react';
import { ProtectedRoute } from '../components/Auth/ProtectedRoute';
import { DashboardLayout } from '../components/Dashboard';

function HelpContent() {
  const [openFaqId, setOpenFaqId] = useState<string | null>(null);

  // FAQ data
  const faqCategories = [
    {
      category: 'Начало работы',
      icon: <Sparkles className="w-5 h-5" />,
      questions: [
        {
          id: 'faq-1',
          question: 'Как начать использовать платформу?',
          answer:
            'После регистрации через Telegram вы попадёте на главную страницу Dashboard. Рекомендуем начать с раздела "Быстрые действия" - создайте свой первый квест, напишите письмо или поставьте цель. AI-ассистент поможет вам на каждом шаге.',
        },
        {
          id: 'faq-2',
          question: 'Что такое треки восстановления?',
          answer:
            'Треки восстановления - это 4 основных направления работы: Работа над собой, Связь с ребёнком, Переговоры и Сообщество. Каждый трек содержит персонализированные задачи и рекомендации, адаптированные под вашу ситуацию.',
        },
        {
          id: 'faq-3',
          question: 'Как работает AI-ассистент?',
          answer:
            'AI-ассистент анализирует вашу ситуацию и создаёт персонализированные квесты, письма и рекомендации. Он учитывает возраст ребёнка, ваши интересы и эмоциональное состояние, чтобы предложить наиболее подходящий контент.',
        },
      ],
    },
    {
      category: 'Квесты',
      icon: <Sparkles className="w-5 h-5" />,
      questions: [
        {
          id: 'faq-4',
          question: 'Что такое образовательные квесты?',
          answer:
            'Образовательные квесты - это интерактивные задания для вашего ребёнка, созданные с учётом его возраста и интересов. Они помогают поддерживать связь через совместное обучение и игру.',
        },
        {
          id: 'faq-5',
          question: 'Как создать квест?',
          answer:
            'Нажмите на кнопку "Создать квест" на главной странице или в разделе "Мои проекты". AI-ассистент задаст вам несколько вопросов о ребёнке и его интересах, после чего создаст персонализированный квест.',
        },
        {
          id: 'faq-6',
          question: 'Можно ли редактировать квесты?',
          answer:
            'Да, вы можете редактировать любой созданный квест. Просто откройте его из списка "Мои проекты" и внесите необходимые изменения. AI-ассистент также может помочь с доработкой.',
        },
      ],
    },
    {
      category: 'Письма',
      icon: <Mail className="w-5 h-5" />,
      questions: [
        {
          id: 'faq-7',
          question: 'Как написать письмо ребёнку?',
          answer:
            'Выберите тип письма (благодарность, извинение, воспоминание или надежда), и AI-ассистент поможет вам структурировать мысли и найти правильные слова. Вы можете писать на русском языке.',
        },
        {
          id: 'faq-8',
          question: 'Как отправить письмо?',
          answer:
            'После написания письма вы можете сохранить его в личном архиве, отправить на email другому родителю для передачи ребёнку, или распечатать. Мы также работаем над функцией безопасной отправки напрямую.',
        },
      ],
    },
    {
      category: 'Конфиденциальность',
      icon: <Heart className="w-5 h-5" />,
      questions: [
        {
          id: 'faq-9',
          question: 'Безопасны ли мои данные?',
          answer:
            'Да, все ваши данные зашифрованы и хранятся в защищённой базе данных. Мы не передаём информацию третьим лицам и соблюдаем все требования GDPR и российского законодательства о персональных данных.',
        },
        {
          id: 'faq-10',
          question: 'Кто имеет доступ к моим квестам и письмам?',
          answer:
            'Только вы имеете доступ к своим квестам и письмам. Мы не модерируем контент и не читаем ваши материалы. Исключение - если вы сами поделитесь ссылкой или отправите контент другому родителю.',
        },
      ],
    },
  ];

  // Support options
  const supportOptions = [
    {
      id: 'chat',
      title: 'Онлайн чат',
      description: 'Напишите нам в чат поддержки',
      icon: <MessageCircle className="w-6 h-6" />,
      action: 'Открыть чат',
      color: 'blue',
    },
    {
      id: 'email',
      title: 'Email поддержка',
      description: 'support@pasinpeace.ru',
      icon: <Mail className="w-6 h-6" />,
      action: 'Написать письмо',
      color: 'purple',
    },
    {
      id: 'telegram',
      title: 'Telegram',
      description: '@pasinpeace_support',
      icon: <Phone className="w-6 h-6" />,
      action: 'Открыть Telegram',
      color: 'cyan',
    },
  ];

  // Quick links
  const quickLinks = [
    {
      title: 'Документация',
      icon: <Book className="w-5 h-5" />,
      href: '#',
    },
    {
      title: 'Видео-туры',
      icon: <Video className="w-5 h-5" />,
      href: '#',
    },
    {
      title: 'Сообщество',
      icon: <MessageCircle className="w-5 h-5" />,
      href: '#',
    },
  ];

  const toggleFaq = (id: string) => {
    setOpenFaqId(openFaqId === id ? null : id);
  };

  return (
    <DashboardLayout title="Помощь">
      {/* Header */}
      <motion.div
        className="text-center mb-12"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="text-6xl mb-4">💡</div>
        <h2 className="text-3xl font-bold text-white mb-2">Как мы можем помочь?</h2>
        <p className="text-white/70">
          Найдите ответы на часто задаваемые вопросы или свяжитесь с поддержкой
        </p>
      </motion.div>

      {/* Support options */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        {supportOptions.map((option) => (
          <motion.div
            key={option.id}
            className="frosted-card hover:scale-105 transition-all cursor-pointer group"
            whileHover={{ y: -4 }}
          >
            <div
              className={`
              w-14 h-14 rounded-xl mb-4 flex items-center justify-center
              ${option.color === 'blue' && 'bg-blue-500/20 text-blue-400'}
              ${option.color === 'purple' && 'bg-purple-500/20 text-purple-400'}
              ${option.color === 'cyan' && 'bg-cyan-500/20 text-cyan-400'}
              group-hover:scale-110 transition-transform
            `}
            >
              {option.icon}
            </div>
            <h3 className="text-lg font-bold text-white mb-2">{option.title}</h3>
            <p className="text-sm text-white/70 mb-4">{option.description}</p>
            <button className="glass-button w-full bg-white/10 hover:bg-white/20 flex items-center justify-center gap-2">
              {option.action}
              <ExternalLink className="w-4 h-4" />
            </button>
          </motion.div>
        ))}
      </motion.div>

      {/* FAQ */}
      <motion.div
        className="mb-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
          <HelpCircle className="w-6 h-6 text-blue-400" />
          Часто задаваемые вопросы
        </h3>

        <div className="space-y-6">
          {faqCategories.map((category, categoryIndex) => (
            <div key={category.category}>
              {/* Category header */}
              <div className="flex items-center gap-2 mb-4">
                <div className="text-purple-400">{category.icon}</div>
                <h4 className="text-lg font-bold text-white">{category.category}</h4>
              </div>

              {/* Questions */}
              <div className="space-y-3">
                {category.questions.map((faq) => (
                  <motion.div
                    key={faq.id}
                    className="frosted-card cursor-pointer"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: categoryIndex * 0.1 }}
                  >
                    <button
                      onClick={() => toggleFaq(faq.id)}
                      className="w-full flex items-start justify-between gap-4 text-left"
                    >
                      <span className="flex-1 font-medium text-white">
                        {faq.question}
                      </span>
                      <motion.div
                        animate={{ rotate: openFaqId === faq.id ? 180 : 0 }}
                        transition={{ duration: 0.2 }}
                      >
                        <ChevronDown className="w-5 h-5 text-white/70 flex-shrink-0" />
                      </motion.div>
                    </button>

                    <AnimatePresence>
                      {openFaqId === faq.id && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.2 }}
                          className="overflow-hidden"
                        >
                          <p className="text-white/70 text-sm mt-4 leading-relaxed">
                            {faq.answer}
                          </p>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Quick links */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h3 className="text-2xl font-bold text-white mb-6">Полезные ресурсы</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {quickLinks.map((link) => (
            <a
              key={link.title}
              href={link.href}
              className="frosted-card hover:scale-105 transition-all flex items-center gap-4 group"
            >
              <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center text-blue-400 group-hover:bg-blue-500/20 transition-colors">
                {link.icon}
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-white group-hover:text-blue-400 transition-colors">
                  {link.title}
                </h4>
              </div>
              <ExternalLink className="w-4 h-4 text-white/50 group-hover:text-white transition-colors" />
            </a>
          ))}
        </div>
      </motion.div>
    </DashboardLayout>
  );
}

export default function HelpPage() {
  return (
    <ProtectedRoute>
      <HelpContent />
    </ProtectedRoute>
  );
}
