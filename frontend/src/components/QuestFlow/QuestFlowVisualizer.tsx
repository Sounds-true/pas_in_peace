/**
 * QuestFlowVisualizer - ReactFlow visualization for quest structure
 *
 * Features:
 * - Interactive node graph
 * - Drag & drop editing (in edit mode)
 * - Different node types (start, question, activity, choice, end)
 * - Real-time preview
 * - Liquid Glass design
 */

import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  MarkerType,
  NodeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion } from 'framer-motion';
import {
  Play,
  HelpCircle,
  Activity,
  GitBranch,
  CheckCircle,
} from 'lucide-react';

export interface QuestFlowNode {
  id: string;
  type: 'start' | 'question' | 'activity' | 'choice' | 'end';
  data: {
    title: string;
    description?: string;
    emoji?: string;
  };
  position: { x: number; y: number };
}

export interface QuestFlowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

export interface QuestFlowVisualizerProps {
  nodes: QuestFlowNode[];
  edges: QuestFlowEdge[];
  mode?: 'view' | 'edit';
  onNodeClick?: (node: QuestFlowNode) => void;
  onNodesChange?: (nodes: QuestFlowNode[]) => void;
  onEdgesChange?: (edges: QuestFlowEdge[]) => void;
  className?: string;
}

// Custom node components
const StartNode: React.FC<{ data: any }> = ({ data }) => (
  <motion.div
    className="px-6 py-4 rounded-2xl bg-gradient-to-br from-green-500/30 to-emerald-500/30 border-2 border-green-400/50 backdrop-blur-xl shadow-2xl min-w-[200px]"
    initial={{ scale: 0 }}
    animate={{ scale: 1 }}
    whileHover={{ scale: 1.05 }}
  >
    <div className="flex items-center gap-3 mb-2">
      <Play className="w-5 h-5 text-green-400" />
      <h4 className="font-bold text-white">Старт</h4>
    </div>
    <p className="text-sm text-white/80">{data.title}</p>
  </motion.div>
);

const QuestionNode: React.FC<{ data: any }> = ({ data }) => (
  <motion.div
    className="px-6 py-4 rounded-2xl bg-gradient-to-br from-blue-500/30 to-cyan-500/30 border-2 border-blue-400/50 backdrop-blur-xl shadow-2xl min-w-[200px]"
    whileHover={{ scale: 1.05 }}
  >
    <div className="flex items-center gap-3 mb-2">
      <HelpCircle className="w-5 h-5 text-blue-400" />
      <h4 className="font-bold text-white">Вопрос</h4>
    </div>
    <p className="text-sm text-white/80">{data.title}</p>
    {data.description && (
      <p className="text-xs text-white/60 mt-2">{data.description}</p>
    )}
  </motion.div>
);

const ActivityNode: React.FC<{ data: any }> = ({ data }) => (
  <motion.div
    className="px-6 py-4 rounded-2xl bg-gradient-to-br from-purple-500/30 to-pink-500/30 border-2 border-purple-400/50 backdrop-blur-xl shadow-2xl min-w-[200px]"
    whileHover={{ scale: 1.05 }}
  >
    <div className="flex items-center gap-3 mb-2">
      {data.emoji && <span className="text-2xl">{data.emoji}</span>}
      <Activity className="w-5 h-5 text-purple-400" />
      <h4 className="font-bold text-white">Задание</h4>
    </div>
    <p className="text-sm text-white/80">{data.title}</p>
    {data.description && (
      <p className="text-xs text-white/60 mt-2">{data.description}</p>
    )}
  </motion.div>
);

const ChoiceNode: React.FC<{ data: any }> = ({ data }) => (
  <motion.div
    className="px-6 py-4 rounded-2xl bg-gradient-to-br from-orange-500/30 to-yellow-500/30 border-2 border-orange-400/50 backdrop-blur-xl shadow-2xl min-w-[200px]"
    whileHover={{ scale: 1.05 }}
  >
    <div className="flex items-center gap-3 mb-2">
      <GitBranch className="w-5 h-5 text-orange-400" />
      <h4 className="font-bold text-white">Выбор</h4>
    </div>
    <p className="text-sm text-white/80">{data.title}</p>
  </motion.div>
);

const EndNode: React.FC<{ data: any }> = ({ data }) => (
  <motion.div
    className="px-6 py-4 rounded-2xl bg-gradient-to-br from-emerald-500/30 to-teal-500/30 border-2 border-emerald-400/50 backdrop-blur-xl shadow-2xl min-w-[200px]"
    whileHover={{ scale: 1.05 }}
  >
    <div className="flex items-center gap-3 mb-2">
      <CheckCircle className="w-5 h-5 text-emerald-400" />
      <h4 className="font-bold text-white">Финиш</h4>
    </div>
    <p className="text-sm text-white/80">{data.title || 'Квест завершён!'}</p>
  </motion.div>
);

const nodeTypes: NodeTypes = {
  start: StartNode,
  question: QuestionNode,
  activity: ActivityNode,
  choice: ChoiceNode,
  end: EndNode,
};

export const QuestFlowVisualizer: React.FC<QuestFlowVisualizerProps> = ({
  nodes: initialNodes,
  edges: initialEdges,
  mode = 'view',
  onNodeClick,
  onNodesChange,
  onEdgesChange,
  className = '',
}) => {
  // Convert to ReactFlow format
  const reactFlowNodes: Node[] = useMemo(
    () =>
      initialNodes.map((node) => ({
        id: node.id,
        type: node.type,
        data: node.data,
        position: node.position,
      })),
    [initialNodes]
  );

  const reactFlowEdges: Edge[] = useMemo(
    () =>
      initialEdges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label,
        type: 'smoothstep',
        animated: true,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#60a5fa',
        },
        style: {
          stroke: '#60a5fa',
          strokeWidth: 2,
        },
      })),
    [initialEdges]
  );

  const [nodes, setNodes, onNodesChangeInternal] = useNodesState(reactFlowNodes);
  const [edges, setEdges, onEdgesChangeInternal] = useEdgesState(reactFlowEdges);

  const onConnect = useCallback(
    (connection: Connection) => {
      if (mode === 'edit') {
        const newEdge = {
          ...connection,
          id: `edge-${connection.source}-${connection.target}`,
          type: 'smoothstep',
          animated: true,
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: '#60a5fa',
          },
        };
        setEdges((eds) => addEdge(newEdge, eds));

        if (onEdgesChange) {
          const convertedEdges = edges.map((e) => ({
            id: e.id,
            source: e.source,
            target: e.target,
            label: e.label,
          }));
          onEdgesChange(convertedEdges as QuestFlowEdge[]);
        }
      }
    },
    [mode, setEdges, edges, onEdgesChange]
  );

  const handleNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      if (onNodeClick) {
        const questNode: QuestFlowNode = {
          id: node.id,
          type: node.type as any,
          data: node.data,
          position: node.position,
        };
        onNodeClick(questNode);
      }
    },
    [onNodeClick]
  );

  return (
    <div className={`relative ${className}`}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={mode === 'edit' ? onNodesChangeInternal : undefined}
        onEdgesChange={mode === 'edit' ? onEdgesChangeInternal : undefined}
        onConnect={onConnect}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
        className="rounded-2xl overflow-hidden"
        style={{
          background: 'rgba(15, 23, 42, 0.5)',
          backdropFilter: 'blur(20px)',
        }}
      >
        <Background
          color="#ffffff"
          gap={16}
          size={1}
          style={{ opacity: 0.1 }}
        />
        <Controls
          className="liquid-glass"
        />
        <MiniMap
          nodeColor={(node) => {
            switch (node.type) {
              case 'start':
                return '#10b981';
              case 'question':
                return '#3b82f6';
              case 'activity':
                return '#a855f7';
              case 'choice':
                return '#f59e0b';
              case 'end':
                return '#14b8a6';
              default:
                return '#64748b';
            }
          }}
          className="liquid-glass"
          style={{
            backgroundColor: 'rgba(15, 23, 42, 0.8)',
          }}
        />
      </ReactFlow>

      {mode === 'view' && (
        <div className="absolute top-4 right-4 frosted-card px-4 py-2">
          <p className="text-xs text-white/70">
            <span className="font-medium text-white">{nodes.length}</span> шагов •{' '}
            <span className="font-medium text-white">{edges.length}</span> переходов
          </p>
        </div>
      )}
    </div>
  );
};

export default QuestFlowVisualizer;
