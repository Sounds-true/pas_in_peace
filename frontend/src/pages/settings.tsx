/**
 * Settings Page - User preferences and account settings
 *
 * Protected route - requires authentication
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  User,
  Bell,
  Lock,
  Palette,
  Globe,
  Trash2,
  Save,
  Camera,
  Mail,
  Phone,
  Shield,
  Eye,
  EyeOff,
} from 'lucide-react';
import { ProtectedRoute } from '../components/Auth/ProtectedRoute';
import { DashboardLayout } from '../components/Dashboard';
import { useUserStore } from '../lib/stores/userStore';

type TabType = 'profile' | 'notifications' | 'privacy' | 'appearance';

function SettingsContent() {
  const { user } = useUserStore();
  const [activeTab, setActiveTab] = useState<TabType>('profile');
  const [isSaving, setIsSaving] = useState(false);

  // Settings state
  const [settings, setSettings] = useState({
    // Profile
    firstName: user?.first_name || '',
    lastName: '', // last_name not in User type
    username: user?.username || '',
    email: '',
    phone: '',
    bio: '',
    // Notifications
    emailNotifications: true,
    questReminders: true,
    milestoneAlerts: true,
    weeklyDigest: true,
    communityUpdates: false,
    // Privacy
    profileVisibility: 'private',
    showActivity: false,
    dataSharing: false,
    // Appearance
    theme: 'dark',
    language: 'ru',
  });

  const handleSave = async () => {
    setIsSaving(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsSaving(false);
    // TODO: Show success toast
  };

  const tabs = [
    {
      id: 'profile' as TabType,
      label: 'Профиль',
      icon: <User className="w-5 h-5" />,
    },
    {
      id: 'notifications' as TabType,
      label: 'Уведомления',
      icon: <Bell className="w-5 h-5" />,
    },
    {
      id: 'privacy' as TabType,
      label: 'Приватность',
      icon: <Lock className="w-5 h-5" />,
    },
    {
      id: 'appearance' as TabType,
      label: 'Внешний вид',
      icon: <Palette className="w-5 h-5" />,
    },
  ];

  return (
    <DashboardLayout
      title="Настройки"
      actions={
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="glass-button bg-blue-500/20 hover:bg-blue-500/30 flex items-center gap-2 disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          {isSaving ? 'Сохранение...' : 'Сохранить'}
        </button>
      }
    >
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar tabs */}
        <motion.div
          className="lg:w-64 flex-shrink-0"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <div className="frosted-card space-y-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  w-full flex items-center gap-3 px-4 py-3 rounded-lg
                  transition-all text-left
                  ${
                    activeTab === tab.id
                      ? 'bg-blue-500/20 text-white'
                      : 'text-white/70 hover:bg-white/10 hover:text-white'
                  }
                `}
              >
                {tab.icon}
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </div>
        </motion.div>

        {/* Content */}
        <motion.div
          className="flex-1"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          key={activeTab}
        >
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="space-y-6">
              <div className="frosted-card">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <User className="w-5 h-5 text-blue-400" />
                  Личная информация
                </h3>

                {/* Avatar */}
                <div className="flex items-center gap-4 mb-6">
                  {user?.photo_url ? (
                    <img
                      src={user.photo_url}
                      alt={user.first_name}
                      className="w-20 h-20 rounded-full border-4 border-white/20"
                    />
                  ) : (
                    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white text-2xl font-bold">
                      {settings.firstName[0]?.toUpperCase() || 'U'}
                    </div>
                  )}
                  <div>
                    <button className="glass-button bg-blue-500/20 hover:bg-blue-500/30 flex items-center gap-2 mb-2">
                      <Camera className="w-4 h-4" />
                      Изменить фото
                    </button>
                    <p className="text-xs text-white/60">
                      PNG, JPG до 5MB
                    </p>
                  </div>
                </div>

                {/* Form fields */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-white/70 mb-2">
                      Имя
                    </label>
                    <input
                      type="text"
                      value={settings.firstName}
                      onChange={(e) =>
                        setSettings({ ...settings, firstName: e.target.value })
                      }
                      className="w-full frosted-card px-4 py-2 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-white/70 mb-2">
                      Фамилия
                    </label>
                    <input
                      type="text"
                      value={settings.lastName}
                      onChange={(e) =>
                        setSettings({ ...settings, lastName: e.target.value })
                      }
                      className="w-full frosted-card px-4 py-2 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-white/70 mb-2">
                      Username
                    </label>
                    <input
                      type="text"
                      value={settings.username}
                      onChange={(e) =>
                        setSettings({ ...settings, username: e.target.value })
                      }
                      className="w-full frosted-card px-4 py-2 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50"
                      disabled
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-white/70 mb-2 flex items-center gap-2">
                      <Mail className="w-4 h-4" />
                      Email
                    </label>
                    <input
                      type="email"
                      value={settings.email}
                      onChange={(e) =>
                        setSettings({ ...settings, email: e.target.value })
                      }
                      placeholder="email@example.com"
                      className="w-full frosted-card px-4 py-2 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-white/70 mb-2 flex items-center gap-2">
                      <Phone className="w-4 h-4" />
                      Телефон
                    </label>
                    <input
                      type="tel"
                      value={settings.phone}
                      onChange={(e) =>
                        setSettings({ ...settings, phone: e.target.value })
                      }
                      placeholder="+7 (999) 123-45-67"
                      className="w-full frosted-card px-4 py-2 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50"
                    />
                  </div>
                </div>

                {/* Bio */}
                <div className="mt-4">
                  <label className="block text-sm font-medium text-white/70 mb-2">
                    О себе
                  </label>
                  <textarea
                    value={settings.bio}
                    onChange={(e) =>
                      setSettings({ ...settings, bio: e.target.value })
                    }
                    rows={4}
                    placeholder="Расскажите немного о себе..."
                    className="w-full frosted-card px-4 py-2 text-white placeholder:text-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50 resize-none"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <div className="frosted-card">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <Bell className="w-5 h-5 text-purple-400" />
                  Уведомления
                </h3>

                <div className="space-y-4">
                  <ToggleSetting
                    label="Email уведомления"
                    description="Получать уведомления на email"
                    checked={settings.emailNotifications}
                    onChange={(checked) =>
                      setSettings({ ...settings, emailNotifications: checked })
                    }
                  />
                  <ToggleSetting
                    label="Напоминания о квестах"
                    description="Уведомления о новых и незавершённых квестах"
                    checked={settings.questReminders}
                    onChange={(checked) =>
                      setSettings({ ...settings, questReminders: checked })
                    }
                  />
                  <ToggleSetting
                    label="Оповещения о целях"
                    description="Напоминания о достижении целей и вех"
                    checked={settings.milestoneAlerts}
                    onChange={(checked) =>
                      setSettings({ ...settings, milestoneAlerts: checked })
                    }
                  />
                  <ToggleSetting
                    label="Еженедельный дайджест"
                    description="Сводка прогресса за неделю"
                    checked={settings.weeklyDigest}
                    onChange={(checked) =>
                      setSettings({ ...settings, weeklyDigest: checked })
                    }
                  />
                  <ToggleSetting
                    label="Новости сообщества"
                    description="Обновления от других родителей"
                    checked={settings.communityUpdates}
                    onChange={(checked) =>
                      setSettings({ ...settings, communityUpdates: checked })
                    }
                  />
                </div>
              </div>
            </div>
          )}

          {/* Privacy Tab */}
          {activeTab === 'privacy' && (
            <div className="space-y-6">
              <div className="frosted-card">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <Shield className="w-5 h-5 text-green-400" />
                  Приватность и безопасность
                </h3>

                <div className="space-y-6">
                  {/* Profile visibility */}
                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      Видимость профиля
                    </label>
                    <select
                      value={settings.profileVisibility}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          profileVisibility: e.target.value,
                        })
                      }
                      className="w-full frosted-card px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-400/50"
                    >
                      <option value="private">Приватный (только я)</option>
                      <option value="community">Сообщество</option>
                      <option value="public">Публичный</option>
                    </select>
                  </div>

                  <ToggleSetting
                    label="Показывать активность"
                    description="Другие пользователи могут видеть вашу активность"
                    checked={settings.showActivity}
                    onChange={(checked) =>
                      setSettings({ ...settings, showActivity: checked })
                    }
                  />
                  <ToggleSetting
                    label="Обмен данными"
                    description="Помогать улучшать платформу анонимными данными"
                    checked={settings.dataSharing}
                    onChange={(checked) =>
                      setSettings({ ...settings, dataSharing: checked })
                    }
                  />

                  {/* Danger zone */}
                  <div className="pt-6 border-t border-white/10">
                    <h4 className="text-lg font-bold text-red-400 mb-4">
                      Опасная зона
                    </h4>
                    <button className="glass-button bg-red-500/20 hover:bg-red-500/30 text-red-400 flex items-center gap-2">
                      <Trash2 className="w-4 h-4" />
                      Удалить аккаунт
                    </button>
                    <p className="text-xs text-white/60 mt-2">
                      Это действие нельзя отменить. Все ваши данные будут удалены.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Appearance Tab */}
          {activeTab === 'appearance' && (
            <div className="space-y-6">
              <div className="frosted-card">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <Palette className="w-5 h-5 text-pink-400" />
                  Внешний вид
                </h3>

                <div className="space-y-6">
                  {/* Theme */}
                  <div>
                    <label className="block text-sm font-medium text-white mb-3">
                      Тема
                    </label>
                    <div className="grid grid-cols-2 gap-4">
                      <button
                        onClick={() => setSettings({ ...settings, theme: 'dark' })}
                        className={`
                          frosted-card p-4 text-left transition-all
                          ${
                            settings.theme === 'dark'
                              ? 'ring-2 ring-blue-400'
                              : 'hover:bg-white/10'
                          }
                        `}
                      >
                        <div className="w-full h-20 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 rounded-lg mb-3" />
                        <h4 className="text-white font-medium">Тёмная</h4>
                        <p className="text-xs text-white/60">Текущая тема</p>
                      </button>
                      <button
                        onClick={() => setSettings({ ...settings, theme: 'light' })}
                        disabled
                        className="frosted-card p-4 text-left opacity-50 cursor-not-allowed"
                      >
                        <div className="w-full h-20 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 rounded-lg mb-3" />
                        <h4 className="text-white font-medium">Светлая</h4>
                        <p className="text-xs text-white/60">Скоро...</p>
                      </button>
                    </div>
                  </div>

                  {/* Language */}
                  <div>
                    <label className="block text-sm font-medium text-white mb-2 flex items-center gap-2">
                      <Globe className="w-4 h-4" />
                      Язык
                    </label>
                    <select
                      value={settings.language}
                      onChange={(e) =>
                        setSettings({ ...settings, language: e.target.value })
                      }
                      className="w-full frosted-card px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-400/50"
                    >
                      <option value="ru">Русский</option>
                      <option value="en">English (Coming soon)</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </DashboardLayout>
  );
}

// Toggle Setting Component
interface ToggleSettingProps {
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

const ToggleSetting: React.FC<ToggleSettingProps> = ({
  label,
  description,
  checked,
  onChange,
}) => {
  return (
    <div className="flex items-start justify-between gap-4 pb-4 border-b border-white/10 last:border-0 last:pb-0">
      <div className="flex-1">
        <h4 className="text-white font-medium mb-1">{label}</h4>
        <p className="text-sm text-white/60">{description}</p>
      </div>
      <button
        onClick={() => onChange(!checked)}
        className={`
          relative w-12 h-6 rounded-full transition-colors flex-shrink-0
          ${checked ? 'bg-blue-500' : 'bg-white/20'}
        `}
      >
        <motion.div
          className="absolute top-1 w-4 h-4 rounded-full bg-white"
          animate={{
            left: checked ? '28px' : '4px',
          }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        />
      </button>
    </div>
  );
};

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsContent />
    </ProtectedRoute>
  );
}
