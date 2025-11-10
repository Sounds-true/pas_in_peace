/**
 * TypeScript types for PAS in Peace application
 */

// ========== User ==========

export interface User {
  id: number;
  telegram_id: string;
  first_name: string;
  username?: string;
  photo_url?: string;
  created_at: string;
  updated_at: string;

  // Profile data
  child_name?: string;
  child_age?: number;
  child_interests?: string[];

  // Settings
  primary_track?: string;
  notification_enabled?: boolean;
}

// ========== Recovery Tracks ==========

export type TrackType = 'SELF_WORK' | 'CHILD_CONNECTION' | 'NEGOTIATION' | 'COMMUNITY';

export type PhaseType =
  | 'PHASE_1_ASSESSMENT'
  | 'PHASE_2_FOUNDATION'
  | 'PHASE_3_ACTIVE_WORK'
  | 'PHASE_4_INTEGRATION';

export interface Milestone {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  completedAt?: string;
}

export interface RecoveryTrack {
  id: string;
  type: TrackType;
  name: string;
  description: string;
  color: string;

  // Progress
  currentPhase: PhaseType;
  progress: number; // 0-100
  milestonesCompleted: number;
  milestonesTotal: number;

  // Milestones
  milestones: Milestone[];

  // Metadata
  isPrimary: boolean;
  startedAt?: string;
  lastActivityAt?: string;
}

// ========== Projects ==========

export type ProjectType = 'quest' | 'letter' | 'goal';
export type ProjectStatus = 'draft' | 'active' | 'completed' | 'moderation';

export interface Project {
  id: string;
  type: ProjectType;
  title: string;
  description?: string;
  status: ProjectStatus;

  // Metadata
  createdAt: string;
  updatedAt: string;
  completedAt?: string;

  // Type-specific data
  data: QuestData | LetterData | GoalData;
}

// ========== Quests ==========

export interface Quest {
  id: string;
  questId: string;
  title: string;
  description?: string;

  // Child info
  childName: string;
  childAge: number;
  childInterests?: string[];

  // Quest structure
  yaml?: string;
  graphStructure?: ReactFlowGraph;
  nodeCount: number;

  // Progress
  progress: number; // 0-100
  status: ProjectStatus;

  // Moderation
  moderationStatus?: 'pending' | 'approved' | 'rejected';
  moderationNotes?: string;

  // Metadata
  createdAt: string;
  updatedAt: string;
  lastPlayedAt?: string;
}

export interface QuestData {
  quest: Quest;
}

export interface ReactFlowGraph {
  nodes: ReactFlowNode[];
  edges: ReactFlowEdge[];
  metadata?: Record<string, any>;
}

export interface ReactFlowNode {
  id: string;
  type: 'start' | 'questStep' | 'choice' | 'realityBridge' | 'end';
  position: { x: number; y: number };
  data: {
    title: string;
    content?: string;
    [key: string]: any;
  };
}

export interface ReactFlowEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
  label?: string;
}

// ========== Letters ==========

export type LetterType = 'gratitude' | 'apology' | 'memory' | 'hope';

export interface Letter {
  id: string;
  type: LetterType;
  title: string;
  content: string;
  status: ProjectStatus;

  // Moderation
  moderationStatus?: 'pending' | 'approved' | 'rejected';
  moderationIssues?: ContentIssue[];

  // Delivery
  sentAt?: string;
  readAt?: string;

  // Metadata
  createdAt: string;
  updatedAt: string;
}

export interface LetterData {
  letter: Letter;
}

export interface ContentIssue {
  category: 'manipulation' | 'emotional_pressure' | 'inappropriate';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  fragments: string[];
  recommendation: string;
}

// ========== Goals ==========

export interface Goal {
  id: string;
  title: string;
  description: string;
  track: TrackType;
  phase: PhaseType;

  // Progress
  status: 'not_started' | 'in_progress' | 'completed' | 'blocked';
  progress: number; // 0-100

  // Tasks
  tasks: Task[];

  // Dates
  dueDate?: string;
  completedAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface GoalData {
  goal: Goal;
}

export interface Task {
  id: string;
  title: string;
  completed: boolean;
  completedAt?: string;
}

// ========== Analytics ==========

export interface AnalyticsData {
  emotionalTrends: EmotionalTrend[];
  trackProgress: TrackProgressData[];
  activitySummary: ActivitySummary;
}

export interface EmotionalTrend {
  date: string;
  mood: 'sad' | 'neutral' | 'happy' | 'excited';
  score: number; // 0-100
}

export interface TrackProgressData {
  trackId: string;
  trackName: string;
  progress: number;
  change: number; // % change from last period
}

export interface ActivitySummary {
  questsCreated: number;
  questsCompleted: number;
  lettersSent: number;
  goalsCompleted: number;
  totalTimeSpent: number; // minutes
}

// ========== WebSocket Messages ==========

export type WSMessageType =
  | 'connected'
  | 'message'
  | 'question'
  | 'quest_preview'
  | 'moderation_warning'
  | 'error';

export interface WSMessage {
  type: WSMessageType;
  content?: string;
  data?: any;
  timestamp?: string;
}

export interface QuestBuilderMessage extends WSMessage {
  type: 'question' | 'quest_preview' | 'moderation_warning';
  data: {
    question?: string;
    options?: string[];
    preview?: ReactFlowGraph;
    warnings?: ContentIssue[];
  };
}

// ========== API Responses ==========

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface ErrorResponse {
  message: string;
  code?: string;
  details?: any;
}

// ========== Auth ==========

export interface TelegramAuthData {
  id: number;
  first_name: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}
