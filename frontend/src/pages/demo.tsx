/**
 * Demo page for Liquid Glass components
 *
 * View all components in action
 */

import React, { useState, useEffect } from 'react';
import {
  QuestCard,
  ProgressRing,
  MultiProgressRing,
  VoiceWave,
  CompactVoiceWave,
  VoiceVisualizer,
} from '../components/LiquidGlass';

export default function DemoPage() {
  const [isRecording, setIsRecording] = useState(false);
  const [amplitude, setAmplitude] = useState(0);

  // Simulate voice amplitude
  useEffect(() => {
    if (isRecording) {
      const interval = setInterval(() => {
        setAmplitude(Math.random() * 0.8 + 0.2);
      }, 100);
      return () => clearInterval(interval);
    } else {
      setAmplitude(0);
    }
  }, [isRecording]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 gradient-text">
            Liquid Glass Components
          </h1>
          <p className="text-white/70 text-lg">
            Демонстрация компонентов для PAS in Peace
          </p>
        </div>

        {/* Section: Quest Cards */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
            <span>📚</span>
            Quest Cards
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <QuestCard
              questId="quest_001"
              title="Тайна зоопарка"
              description="Приключение про жирафов и котиков, где Маша узнает интересные факты о животных"
              childName="Маша"
              childAge={9}
              progress={45}
              status="active"
              nodeCount={6}
              lastUpdated={new Date()}
              onClick={() => alert('Quest clicked!')}
            />

            <QuestCard
              questId="quest_002"
              title="Секретный торт"
              description="Кулинарное приключение с математическими задачками"
              childName="Маша"
              childAge={9}
              progress={100}
              status="completed"
              nodeCount={8}
              lastUpdated={new Date(Date.now() - 86400000)}
              onClick={() => alert('Quest clicked!')}
            />

            <QuestCard
              questId="quest_003"
              title="Природа вокруг нас"
              description="Исследование растений и экосистем"
              childName="Маша"
              childAge={9}
              progress={0}
              status="draft"
              nodeCount={5}
              lastUpdated={new Date(Date.now() - 172800000)}
              onClick={() => alert('Quest clicked!')}
            />

            <QuestCard
              questId="quest_004"
              title="Волшебная математика"
              description="Квест с проверкой модератором"
              childName="Маша"
              childAge={9}
              progress={20}
              status="moderation"
              nodeCount={7}
              lastUpdated={new Date()}
              onClick={() => alert('Quest clicked!')}
            />
          </div>
        </section>

        {/* Section: Progress Rings */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
            <span>📊</span>
            Progress Rings
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
            <div className="flex flex-col items-center gap-4">
              <ProgressRing
                progress={25}
                color="#60a5fa"
                glowColor="#3b82f6"
                label="Начало"
              />
              <p className="text-white/70 text-sm">25% - Начальная стадия</p>
            </div>

            <div className="flex flex-col items-center gap-4">
              <ProgressRing
                progress={50}
                color="#a78bfa"
                glowColor="#8b5cf6"
                label="Половина"
              />
              <p className="text-white/70 text-sm">50% - На полпути</p>
            </div>

            <div className="flex flex-col items-center gap-4">
              <ProgressRing
                progress={75}
                color="#f472b6"
                glowColor="#ec4899"
                label="Почти готово"
              />
              <p className="text-white/70 text-sm">75% - Близко к цели</p>
            </div>

            <div className="flex flex-col items-center gap-4">
              <ProgressRing
                progress={100}
                color="#34d399"
                glowColor="#10b981"
                label="Завершено"
              />
              <p className="text-white/70 text-sm">100% - Цель достигнута!</p>
            </div>
          </div>

          {/* Multi Progress Ring */}
          <div className="flex justify-center">
            <div className="frosted-card inline-block">
              <h3 className="text-xl font-bold text-white mb-8 text-center">
                4 трека восстановления
              </h3>
              <MultiProgressRing
                tracks={[
                  { id: 'self', name: 'Работа над собой', progress: 65, color: '#60a5fa' },
                  { id: 'child', name: 'Связь с ребёнком', progress: 45, color: '#a78bfa' },
                  { id: 'negotiation', name: 'Переговоры', progress: 30, color: '#f472b6' },
                  { id: 'community', name: 'Сообщество', progress: 50, color: '#34d399' },
                ]}
                size={240}
              />
            </div>
          </div>
        </section>

        {/* Section: Voice Components */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
            <span>🎤</span>
            Voice Interface
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Voice Wave */}
            <div className="frosted-card">
              <h3 className="text-xl font-bold text-white mb-4">Voice Wave</h3>
              <VoiceWave
                isRecording={isRecording}
                amplitude={amplitude}
                onToggleRecording={() => setIsRecording(!isRecording)}
              />
            </div>

            {/* Voice Visualizer */}
            <div className="frosted-card">
              <h3 className="text-xl font-bold text-white mb-4">Voice Visualizer</h3>
              <div className="flex items-center justify-center h-64">
                <VoiceVisualizer
                  amplitude={amplitude}
                  size={200}
                />
              </div>
            </div>
          </div>

          {/* Compact Voice Waves */}
          <div className="frosted-card mt-8">
            <h3 className="text-xl font-bold text-white mb-6">Compact Voice Waves</h3>
            <div className="flex items-center justify-around">
              <div className="text-center">
                <CompactVoiceWave isActive={isRecording} size="sm" />
                <p className="text-white/60 text-xs mt-2">Small</p>
              </div>
              <div className="text-center">
                <CompactVoiceWave isActive={isRecording} size="md" />
                <p className="text-white/60 text-xs mt-2">Medium</p>
              </div>
              <div className="text-center">
                <CompactVoiceWave isActive={isRecording} size="lg" />
                <p className="text-white/60 text-xs mt-2">Large</p>
              </div>
            </div>
          </div>
        </section>

        {/* Section: Glass UI Elements */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
            <span>✨</span>
            Glass UI Elements
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Buttons */}
            <div className="frosted-card">
              <h3 className="text-lg font-bold text-white mb-4">Кнопки</h3>
              <div className="flex flex-wrap gap-3">
                <button className="glass-button">
                  Создать квест
                </button>
                <button className="glass-button bg-blue-500/20">
                  Написать письмо
                </button>
                <button className="glass-button bg-green-500/20">
                  Сохранить
                </button>
                <button className="glass-button bg-red-500/20">
                  Удалить
                </button>
              </div>
            </div>

            {/* Inputs */}
            <div className="frosted-card">
              <h3 className="text-lg font-bold text-white mb-4">Поля ввода</h3>
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="Введите имя ребёнка..."
                  className="glass-input"
                />
                <input
                  type="number"
                  placeholder="Возраст"
                  className="glass-input"
                />
                <textarea
                  placeholder="Описание квеста..."
                  className="glass-input resize-none"
                  rows={3}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="text-center text-white/50 text-sm py-8 border-t border-white/10">
          <p>PAS in Peace © 2025 • Liquid Glass Components v0.1.0</p>
        </footer>
      </div>
    </div>
  );
}
