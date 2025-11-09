# Mind Map Advanced UX - Quest Builder Visual Editor

## 🎯 Overview

Продвинутый визуальный редактор квестов на базе mind map интерфейса, позволяющий родителям создавать сложные разветвленные квесты через интуитивный drag-and-drop интерфейс с продвинутой навигацией и UX-решениями.

**Референсы:**
- [Notare.uk](https://notare.uk) - advanced mind mapping
- Miro/Figma - infinite canvas pattern
- Obsidian Graph View - связи и навигация
- Apple Maps - gesture controls

---

## 🏗️ Architecture

### Tech Stack

```typescript
// Core
- React Flow v11+ (graph engine)
- Zustand (state management)
- D3.js (custom layouts)
- Framer Motion (animations)
- React DnD (drag-and-drop)

// Canvas
- HTML5 Canvas API (minimap)
- IntersectionObserver (performance)
- ResizeObserver (responsive)

// UI
- Radix UI (context menus, popovers)
- Tailwind + Liquid Glass (styling)
- Lucide React (icons)
```

### Component Hierarchy

```
MindMapEditor/
├── Canvas/
│   ├── InfiniteCanvas (viewport, zoom, pan)
│   ├── NodeLayer (quest nodes rendering)
│   ├── EdgeLayer (connections rendering)
│   ├── SelectionLayer (multi-select, lasso)
│   └── GhostLayer (drag preview)
├── Navigation/
│   ├── MiniMap (overview + quick jump)
│   ├── ZoomControls (zoom in/out/fit)
│   ├── SearchPanel (find nodes)
│   └── BreadcrumbTrail (path history)
├── Sidebar/
│   ├── NodePalette (templates library)
│   ├── PropertiesPanel (node editing)
│   ├── StructureOutline (tree view)
│   └── ValidationPanel (errors/warnings)
├── Toolbar/
│   ├── QuickActions (undo/redo/copy/paste)
│   ├── LayoutControls (auto-arrange)
│   ├── ViewModes (focus/overview/preview)
│   └── AIAssistant (story mode toggle)
└── ContextMenu/
    ├── NodeActions
    ├── EdgeActions
    └── CanvasActions
```

---

## 🎨 Node System

### Node Types

```typescript
type NodeType =
  | 'start'           // 🚪 Старт квеста (1 на граф)
  | 'story'           // 📖 Сюжетная сцена
  | 'challenge'       // 🎯 Образовательный вызов
  | 'puzzle'          // 🧩 Головоломка
  | 'choice'          // 🔀 Развилка (multiple edges out)
  | 'reveal'          // ✨ Reveal момент
  | 'checkpoint'      // 💾 Сохранение прогресса
  | 'end'             // 🏁 Финал (может быть несколько)
  | 'group'           // 📦 Группа нод (для организации)

interface QuestNode {
  id: string;
  type: NodeType;
  position: { x: number; y: number };
  data: {
    // Visual
    title: string;
    description?: string;
    icon?: string;
    color?: string;
    badges?: Array<'voice' | 'psychologist' | 'photo' | 'ai'>;

    // Content
    content: NodeContent;  // Type-specific content

    // Metadata
    estimatedDuration?: number;  // minutes
    difficulty?: 1 | 2 | 3 | 4 | 5;
    requiredAge?: number;
    tags?: string[];

    // Validation
    errors?: ValidationError[];
    warnings?: ValidationWarning[];

    // Analytics
    completionRate?: number;  // 0-100%
    averageTime?: number;     // seconds
  };
}
```

### Visual States

```css
/* Node Visual States */
.node {
  /* Base glass style */
  background: var(--glass-surface);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* State: Default */
.node--default {
  border: 1.5px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* State: Hover */
.node--hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  border-color: var(--accent-primary);
}

/* State: Selected */
.node--selected {
  border: 2px solid var(--accent-primary);
  box-shadow:
    0 4px 16px rgba(0, 122, 255, 0.2),
    0 0 0 4px rgba(0, 122, 255, 0.1);
}

/* State: Dragging */
.node--dragging {
  opacity: 0.8;
  cursor: grabbing;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16);
}

/* State: Error */
.node--error {
  border-color: var(--accent-danger);
  animation: shake 0.4s ease-in-out;
}

/* State: Warning */
.node--warning {
  border-left: 4px solid var(--accent-warning);
}

/* State: Valid */
.node--valid {
  border-left: 4px solid var(--accent-success);
}

/* State: Connecting (during edge creation) */
.node--connecting-source {
  box-shadow: 0 0 0 8px rgba(0, 122, 255, 0.2);
  animation: pulse-ring 1.5s ease-in-out infinite;
}

.node--connecting-target-valid {
  border-color: var(--accent-success);
  box-shadow: 0 0 0 6px rgba(52, 199, 89, 0.2);
}

.node--connecting-target-invalid {
  border-color: var(--accent-danger);
  pointer-events: none;
  opacity: 0.5;
}
```

### Node Component

```typescript
interface NodeProps {
  id: string;
  data: QuestNode['data'];
  type: NodeType;
  isSelected: boolean;
  isHovered: boolean;
  isDragging: boolean;
  isConnecting: boolean;
}

export const QuestNodeComponent: React.FC<NodeProps> = ({
  id,
  data,
  type,
  isSelected,
  ...states
}) => {
  const nodeIcon = getNodeIcon(type);
  const nodeColor = data.color || getDefaultColor(type);

  return (
    <motion.div
      className={cn(
        'quest-node glass-card',
        `node-type-${type}`,
        {
          'node--selected': isSelected,
          'node--hover': states.isHovered,
          'node--dragging': states.isDragging,
          'node--error': data.errors?.length > 0,
          'node--warning': data.warnings?.length > 0,
        }
      )}
      layout
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.8, opacity: 0 }}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.98 }}
      style={{
        borderLeftColor: nodeColor,
      }}
    >
      {/* Header */}
      <div className="node-header">
        <div className="node-icon" style={{ color: nodeColor }}>
          {nodeIcon}
        </div>
        <div className="node-title">{data.title}</div>
        {data.badges && (
          <div className="node-badges">
            {data.badges.map(badge => (
              <Badge key={badge} type={badge} />
            ))}
          </div>
        )}
      </div>

      {/* Content Preview */}
      {data.description && (
        <div className="node-description">
          {truncate(data.description, 80)}
        </div>
      )}

      {/* Metadata */}
      <div className="node-metadata">
        {data.estimatedDuration && (
          <MetadataItem icon="⏱️" value={`${data.estimatedDuration}m`} />
        )}
        {data.difficulty && (
          <MetadataItem
            icon="📊"
            value={<DifficultyStars level={data.difficulty} />}
          />
        )}
      </div>

      {/* Validation Indicators */}
      {data.errors && data.errors.length > 0 && (
        <ValidationIndicator type="error" count={data.errors.length} />
      )}
      {data.warnings && data.warnings.length > 0 && (
        <ValidationIndicator type="warning" count={data.warnings.length} />
      )}

      {/* Connection Handles */}
      <Handle type="target" position="left" />
      <Handle type="source" position="right" />

      {/* Quick Actions (on hover) */}
      <AnimatePresence>
        {states.isHovered && (
          <motion.div
            className="node-quick-actions"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <IconButton icon="edit" onClick={() => onEdit(id)} />
            <IconButton icon="copy" onClick={() => onDuplicate(id)} />
            <IconButton icon="trash" onClick={() => onDelete(id)} />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};
```

---

## 🔗 Edge System

### Edge Types

```typescript
type EdgeType =
  | 'sequence'        // ➡️ Простая последовательность
  | 'conditional'     // 🔀 Условный переход
  | 'fallback'        // ↩️ Запасной путь
  | 'return'          // 🔄 Возврат к предыдущему
  | 'jump'            // ⚡ Телепорт к отдаленной ноде

interface QuestEdge {
  id: string;
  type: EdgeType;
  source: string;      // node id
  target: string;      // node id
  sourceHandle?: string;
  targetHandle?: string;

  data: {
    // Conditional logic
    condition?: EdgeCondition;

    // Visual
    label?: string;
    color?: string;
    animated?: boolean;

    // Analytics
    traversalRate?: number;  // % of users who took this path
  };
}

interface EdgeCondition {
  type: 'score' | 'answer' | 'time' | 'random' | 'custom';
  operator: '>' | '<' | '==' | '!=' | 'contains';
  value: any;
  description: string;
}
```

### Edge Rendering

```typescript
export const QuestEdgeComponent: React.FC<EdgeProps> = ({
  id,
  source,
  target,
  sourceX,
  sourceY,
  targetX,
  targetY,
  data,
  type,
  selected,
}) => {
  // Bezier curve path
  const edgePath = getBezierPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition: 'right',
    targetPosition: 'left',
  });

  const edgeColor = data.color || getDefaultEdgeColor(type);

  return (
    <g className={cn('quest-edge', { 'edge--selected': selected })}>
      {/* Background (wider, for easier selection) */}
      <path
        d={edgePath}
        fill="none"
        stroke="transparent"
        strokeWidth={20}
        className="edge-hitbox"
      />

      {/* Main path */}
      <path
        d={edgePath}
        fill="none"
        stroke={edgeColor}
        strokeWidth={2}
        strokeDasharray={type === 'conditional' ? '8 4' : undefined}
        className={cn('edge-path', {
          'edge-path--animated': data.animated,
        })}
      />

      {/* Arrow marker */}
      <defs>
        <marker
          id={`arrow-${id}`}
          markerWidth="10"
          markerHeight="10"
          refX="8"
          refY="3"
          orient="auto"
          markerUnits="strokeWidth"
        >
          <path d="M0,0 L0,6 L9,3 z" fill={edgeColor} />
        </marker>
      </defs>

      {/* Label */}
      {data.label && (
        <EdgeLabel
          x={(sourceX + targetX) / 2}
          y={(sourceY + targetY) / 2}
          label={data.label}
        />
      )}

      {/* Condition indicator */}
      {data.condition && (
        <EdgeConditionBadge
          x={(sourceX + targetX) / 2}
          y={(sourceY + targetY) / 2 - 20}
          condition={data.condition}
        />
      )}

      {/* Analytics (traversal rate) */}
      {data.traversalRate !== undefined && (
        <EdgeAnalytics
          x={(sourceX + targetX) / 2}
          y={(sourceY + targetY) / 2 + 20}
          rate={data.traversalRate}
        />
      )}
    </g>
  );
};
```

---

## 🎮 Advanced Navigation

### 1. Infinite Canvas

```typescript
interface CanvasState {
  // Viewport
  viewport: {
    x: number;
    y: number;
    zoom: number;  // 0.1 - 2.0
  };

  // Bounds (auto-calculated from nodes)
  bounds: {
    minX: number;
    minY: number;
    maxX: number;
    maxY: number;
  };

  // Performance
  visibleNodes: Set<string>;  // Only render visible
  renderQuality: 'high' | 'medium' | 'low';  // Based on zoom
}

// Gesture Controls (like Apple Maps)
const useCanvasGestures = () => {
  // Pan: Click + Drag (or two-finger trackpad)
  const onPan = usePanGesture({
    onMove: ({ delta: [dx, dy] }) => {
      updateViewport({
        x: viewport.x + dx,
        y: viewport.y + dy,
      });
    },
  });

  // Zoom: Scroll (or pinch gesture)
  const onZoom = useWheelGesture({
    onWheel: ({ delta: [, dy], event }) => {
      event.preventDefault();
      const zoomDelta = -dy * 0.001;
      const newZoom = clamp(
        viewport.zoom * (1 + zoomDelta),
        0.1,
        2.0
      );

      // Zoom to cursor position
      const cursorX = event.clientX;
      const cursorY = event.clientY;

      updateViewport({
        zoom: newZoom,
        x: viewport.x + (cursorX - viewport.x) * (1 - newZoom / viewport.zoom),
        y: viewport.y + (cursorY - viewport.y) * (1 - newZoom / viewport.zoom),
      });
    },
  });

  // Double-click: Zoom in centered
  const onDoubleClick = (event: React.MouseEvent) => {
    const targetZoom = viewport.zoom < 1 ? 1 : 0.5;
    animateViewport({
      zoom: targetZoom,
      x: event.clientX,
      y: event.clientY,
      duration: 300,
    });
  };

  return { onPan, onZoom, onDoubleClick };
};
```

### 2. MiniMap Component

```typescript
interface MiniMapProps {
  nodes: QuestNode[];
  edges: QuestEdge[];
  viewport: CanvasState['viewport'];
  onViewportChange: (viewport: Viewport) => void;
}

export const MiniMap: React.FC<MiniMapProps> = ({
  nodes,
  edges,
  viewport,
  onViewportChange,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Render minimap on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d')!;
    const scale = 0.1;  // Minimap scale factor

    // Clear
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw edges (thin lines)
    ctx.strokeStyle = 'rgba(0, 122, 255, 0.3)';
    ctx.lineWidth = 1;
    edges.forEach(edge => {
      const sourceNode = nodes.find(n => n.id === edge.source);
      const targetNode = nodes.find(n => n.id === edge.target);
      if (!sourceNode || !targetNode) return;

      ctx.beginPath();
      ctx.moveTo(sourceNode.position.x * scale, sourceNode.position.y * scale);
      ctx.lineTo(targetNode.position.x * scale, targetNode.position.y * scale);
      ctx.stroke();
    });

    // Draw nodes (small rectangles)
    nodes.forEach(node => {
      const color = getNodeColor(node.type);
      ctx.fillStyle = color;
      ctx.fillRect(
        node.position.x * scale - 2,
        node.position.y * scale - 2,
        4,
        4
      );
    });

    // Draw viewport rectangle
    ctx.strokeStyle = 'rgba(0, 122, 255, 0.8)';
    ctx.lineWidth = 2;
    ctx.strokeRect(
      viewport.x * scale,
      viewport.y * scale,
      (window.innerWidth / viewport.zoom) * scale,
      (window.innerHeight / viewport.zoom) * scale
    );
  }, [nodes, edges, viewport]);

  // Click on minimap to jump
  const onMinimapClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current!;
    const rect = canvas.getBoundingClientRect();
    const x = (event.clientX - rect.left) / 0.1;
    const y = (event.clientY - rect.top) / 0.1;

    onViewportChange({
      x: x - window.innerWidth / viewport.zoom / 2,
      y: y - window.innerHeight / viewport.zoom / 2,
      zoom: viewport.zoom,
    });
  };

  return (
    <div className="minimap glass-card">
      <canvas
        ref={canvasRef}
        width={200}
        height={150}
        onClick={onMinimapClick}
        onMouseDown={() => setIsDragging(true)}
        onMouseUp={() => setIsDragging(false)}
        onMouseMove={(e) => isDragging && onMinimapClick(e)}
        className="minimap-canvas"
      />
    </div>
  );
};
```

### 3. Search & Quick Jump

```typescript
interface SearchPanelProps {
  nodes: QuestNode[];
  onNodeSelect: (nodeId: string) => void;
}

export const SearchPanel: React.FC<SearchPanelProps> = ({
  nodes,
  onNodeSelect,
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<QuestNode[]>([]);

  // Fuzzy search
  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }

    const fuse = new Fuse(nodes, {
      keys: ['data.title', 'data.description', 'data.tags'],
      threshold: 0.4,
    });

    const searchResults = fuse.search(query).map(r => r.item);
    setResults(searchResults);
  }, [query, nodes]);

  // Keyboard shortcuts
  useKeyboardShortcut('cmd+f', () => {
    focusSearchInput();
  });

  return (
    <div className="search-panel glass-card">
      {/* Search Input */}
      <div className="search-input-wrapper">
        <MagnifyingGlassIcon />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Поиск нод (⌘F)..."
          className="search-input"
        />
        {query && (
          <button onClick={() => setQuery('')}>
            <XIcon />
          </button>
        )}
      </div>

      {/* Results */}
      <AnimatePresence>
        {results.length > 0 && (
          <motion.div
            className="search-results"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            {results.map((node) => (
              <SearchResultItem
                key={node.id}
                node={node}
                onClick={() => {
                  onNodeSelect(node.id);
                  setQuery('');
                }}
                highlight={query}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Search result item with highlight
const SearchResultItem: React.FC<{
  node: QuestNode;
  onClick: () => void;
  highlight: string;
}> = ({ node, onClick, highlight }) => {
  const icon = getNodeIcon(node.type);
  const highlightedTitle = highlightText(node.data.title, highlight);

  return (
    <motion.button
      className="search-result-item"
      onClick={onClick}
      whileHover={{ x: 4 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="result-icon">{icon}</div>
      <div className="result-content">
        <div className="result-title" dangerouslySetInnerHTML={{ __html: highlightedTitle }} />
        <div className="result-meta">
          <NodeTypeBadge type={node.type} />
          {node.data.tags && (
            <span className="result-tags">
              {node.data.tags.slice(0, 2).join(', ')}
            </span>
          )}
        </div>
      </div>
      <ArrowRightIcon className="result-arrow" />
    </motion.button>
  );
};
```

### 4. Breadcrumb Trail

```typescript
// Track navigation history
const useBreadcrumbTrail = () => {
  const [trail, setTrail] = useState<Array<{
    nodeId: string;
    timestamp: number;
  }>>([]);

  const addToTrail = (nodeId: string) => {
    setTrail(prev => [
      ...prev.slice(-9),  // Keep last 10
      { nodeId, timestamp: Date.now() },
    ]);
  };

  const goBack = () => {
    if (trail.length < 2) return;
    const previous = trail[trail.length - 2];
    focusNode(previous.nodeId);
    setTrail(prev => prev.slice(0, -1));
  };

  return { trail, addToTrail, goBack };
};

export const BreadcrumbTrail: React.FC<{
  trail: Array<{ nodeId: string; timestamp: number }>;
  nodes: QuestNode[];
  onNodeClick: (nodeId: string) => void;
}> = ({ trail, nodes, onNodeClick }) => {
  if (trail.length === 0) return null;

  return (
    <div className="breadcrumb-trail glass-card">
      {trail.map((item, index) => {
        const node = nodes.find(n => n.id === item.nodeId);
        if (!node) return null;

        return (
          <React.Fragment key={`${item.nodeId}-${item.timestamp}`}>
            <button
              className="breadcrumb-item"
              onClick={() => onNodeClick(item.nodeId)}
            >
              {getNodeIcon(node.type)}
              <span>{truncate(node.data.title, 20)}</span>
            </button>
            {index < trail.length - 1 && (
              <ChevronRightIcon className="breadcrumb-separator" />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
```

---

## 🎯 Focus Mode

Режим концентрации на одной части графа.

```typescript
interface FocusModeState {
  enabled: boolean;
  focusedNodeId: string | null;
  depth: number;  // How many levels to show (1-3)
  dimOthers: boolean;
}

const useFocusMode = () => {
  const [focusState, setFocusState] = useState<FocusModeState>({
    enabled: false,
    focusedNodeId: null,
    depth: 2,
    dimOthers: true,
  });

  const enterFocusMode = (nodeId: string, depth: number = 2) => {
    // Get related nodes (within depth)
    const relatedNodes = getRelatedNodes(nodeId, depth);

    // Animate: zoom to focused node, dim others
    animateViewport({
      target: nodeId,
      zoom: 1.2,
      duration: 500,
    });

    setFocusState({
      enabled: true,
      focusedNodeId: nodeId,
      depth,
      dimOthers: true,
    });

    // Apply visual effects
    nodes.forEach(node => {
      if (relatedNodes.has(node.id)) {
        node.style.opacity = 1;
      } else {
        node.style.opacity = 0.2;
        node.style.pointerEvents = 'none';
      }
    });
  };

  const exitFocusMode = () => {
    // Reset all nodes
    nodes.forEach(node => {
      node.style.opacity = 1;
      node.style.pointerEvents = 'auto';
    });

    // Zoom out to fit all
    fitView({ duration: 500 });

    setFocusState({
      enabled: false,
      focusedNodeId: null,
      depth: 2,
      dimOthers: true,
    });
  };

  return { focusState, enterFocusMode, exitFocusMode };
};

// UI Control
export const FocusModeButton: React.FC<{
  selectedNodeId: string | null;
  onEnter: (nodeId: string) => void;
  onExit: () => void;
}> = ({ selectedNodeId, onEnter, onExit }) => {
  const [isActive, setIsActive] = useState(false);

  return (
    <Tooltip content="Focus Mode (F)">
      <IconButton
        icon={isActive ? "eye-off" : "eye"}
        onClick={() => {
          if (isActive) {
            onExit();
            setIsActive(false);
          } else if (selectedNodeId) {
            onEnter(selectedNodeId);
            setIsActive(true);
          }
        }}
        disabled={!selectedNodeId && !isActive}
        variant={isActive ? "primary" : "ghost"}
      />
    </Tooltip>
  );
};
```

---

## 🔧 Auto-Layout

Автоматическое расположение нод.

```typescript
type LayoutAlgorithm =
  | 'hierarchical'  // Top-to-bottom tree (default)
  | 'radial'        // Circular layout
  | 'force'         // Physics-based (D3 force)
  | 'dagre'         // Directed acyclic graph

const useAutoLayout = () => {
  const applyLayout = async (
    algorithm: LayoutAlgorithm = 'hierarchical',
    options?: LayoutOptions
  ) => {
    const { nodes, edges } = getGraphData();

    let newPositions: Record<string, { x: number; y: number }>;

    switch (algorithm) {
      case 'hierarchical':
        newPositions = await layoutHierarchical(nodes, edges, options);
        break;
      case 'radial':
        newPositions = await layoutRadial(nodes, edges, options);
        break;
      case 'force':
        newPositions = await layoutForce(nodes, edges, options);
        break;
      case 'dagre':
        newPositions = await layoutDagre(nodes, edges, options);
        break;
    }

    // Animate nodes to new positions
    nodes.forEach(node => {
      const newPos = newPositions[node.id];
      animateNode(node.id, {
        position: newPos,
        duration: 600,
        easing: 'easeOutCubic',
      });
    });
  };

  return { applyLayout };
};

// Hierarchical Layout (default for quests)
const layoutHierarchical = async (
  nodes: QuestNode[],
  edges: QuestEdge[],
  options?: { spacing?: { x: number; y: number } }
): Promise<Record<string, Position>> => {
  const spacing = options?.spacing || { x: 250, y: 200 };
  const positions: Record<string, Position> = {};

  // Find start node
  const startNode = nodes.find(n => n.type === 'start');
  if (!startNode) throw new Error('No start node found');

  // Build tree structure
  const tree = buildTree(startNode.id, edges);

  // Assign levels (BFS)
  const levels: Map<number, string[]> = new Map();
  const queue: Array<{ nodeId: string; level: number }> = [
    { nodeId: startNode.id, level: 0 },
  ];
  const visited = new Set<string>();

  while (queue.length > 0) {
    const { nodeId, level } = queue.shift()!;
    if (visited.has(nodeId)) continue;
    visited.add(nodeId);

    if (!levels.has(level)) levels.set(level, []);
    levels.get(level)!.push(nodeId);

    // Add children
    const children = tree.get(nodeId) || [];
    children.forEach(childId => {
      queue.push({ nodeId: childId, level: level + 1 });
    });
  }

  // Calculate positions
  levels.forEach((nodeIds, level) => {
    const levelWidth = nodeIds.length * spacing.x;
    const startX = -levelWidth / 2;

    nodeIds.forEach((nodeId, index) => {
      positions[nodeId] = {
        x: startX + index * spacing.x + spacing.x / 2,
        y: level * spacing.y,
      };
    });
  });

  return positions;
};
```

---

## ✨ Advanced Features

### 1. Multi-Select & Group Operations

```typescript
const useMultiSelect = () => {
  const [selectedNodes, setSelectedNodes] = useState<Set<string>>(new Set());
  const [isLassoActive, setIsLassoActive] = useState(false);

  // Lasso selection (drag to select multiple)
  const onLassoStart = (event: React.MouseEvent) => {
    if (!event.shiftKey) return;
    setIsLassoActive(true);
    // ... lasso logic
  };

  // Keyboard shortcuts
  useKeyboardShortcut('cmd+a', () => {
    // Select all
    setSelectedNodes(new Set(nodes.map(n => n.id)));
  });

  useKeyboardShortcut('cmd+g', () => {
    // Group selected
    if (selectedNodes.size > 1) {
      createGroup(Array.from(selectedNodes));
    }
  });

  // Bulk operations
  const bulkDelete = () => {
    deleteNodes(Array.from(selectedNodes));
    setSelectedNodes(new Set());
  };

  const bulkDuplicate = () => {
    const duplicates = duplicateNodes(Array.from(selectedNodes));
    setSelectedNodes(new Set(duplicates.map(n => n.id)));
  };

  const bulkSetProperty = (property: string, value: any) => {
    updateNodes(Array.from(selectedNodes), { [property]: value });
  };

  return {
    selectedNodes,
    setSelectedNodes,
    isLassoActive,
    onLassoStart,
    bulkDelete,
    bulkDuplicate,
    bulkSetProperty,
  };
};
```

### 2. Collaborative Editing (Multiplayer)

```typescript
// Real-time collaboration via WebSocket
interface CollaborationState {
  users: Map<string, {
    id: string;
    name: string;
    color: string;
    cursor: { x: number; y: number } | null;
    selectedNodes: string[];
  }>;
}

const useCollaboration = (questId: string) => {
  const [collabState, setCollabState] = useState<CollaborationState>({
    users: new Map(),
  });

  const ws = useWebSocket(`wss://api.innerworld.com/collab/${questId}`);

  // Send local changes
  const broadcastChange = (change: GraphChange) => {
    ws.send({
      type: 'change',
      userId: currentUser.id,
      change,
    });
  };

  // Receive remote changes
  useEffect(() => {
    ws.on('change', (data: { userId: string; change: GraphChange }) => {
      if (data.userId === currentUser.id) return;

      applyRemoteChange(data.change);

      // Show user indicator
      showUserIndicator(data.userId, data.change);
    });

    ws.on('cursor', (data: { userId: string; x: number; y: number }) => {
      updateUserCursor(data.userId, { x: data.x, y: data.y });
    });
  }, [ws]);

  return { collabState, broadcastChange };
};

// Render other users' cursors
const CollaborativeCursors: React.FC<{
  users: CollaborationState['users'];
}> = ({ users }) => {
  return (
    <>
      {Array.from(users.values()).map(user => (
        user.cursor && (
          <motion.div
            key={user.id}
            className="collab-cursor"
            style={{
              left: user.cursor.x,
              top: user.cursor.y,
              borderColor: user.color,
            }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
          >
            <div className="cursor-arrow" style={{ background: user.color }} />
            <div className="cursor-label glass-card" style={{ background: user.color }}>
              {user.name}
            </div>
          </motion.div>
        )
      ))}
    </>
  );
};
```

### 3. Version History & Undo/Redo

```typescript
interface GraphSnapshot {
  id: string;
  timestamp: number;
  nodes: QuestNode[];
  edges: QuestEdge[];
  description: string;
}

const useVersionHistory = () => {
  const [history, setHistory] = useState<GraphSnapshot[]>([]);
  const [currentIndex, setCurrentIndex] = useState(-1);

  // Save snapshot
  const saveSnapshot = (description: string = 'Manual save') => {
    const snapshot: GraphSnapshot = {
      id: nanoid(),
      timestamp: Date.now(),
      nodes: cloneDeep(nodes),
      edges: cloneDeep(edges),
      description,
    };

    setHistory(prev => [...prev, snapshot]);
    setCurrentIndex(history.length);
  };

  // Undo
  const undo = () => {
    if (currentIndex <= 0) return;

    const previousSnapshot = history[currentIndex - 1];
    restoreSnapshot(previousSnapshot);
    setCurrentIndex(currentIndex - 1);
  };

  // Redo
  const redo = () => {
    if (currentIndex >= history.length - 1) return;

    const nextSnapshot = history[currentIndex + 1];
    restoreSnapshot(nextSnapshot);
    setCurrentIndex(currentIndex + 1);
  };

  // Keyboard shortcuts
  useKeyboardShortcut('cmd+z', undo);
  useKeyboardShortcut('cmd+shift+z', redo);

  return { history, currentIndex, saveSnapshot, undo, redo };
};

// UI: Version History Panel
export const VersionHistoryPanel: React.FC<{
  history: GraphSnapshot[];
  currentIndex: number;
  onRestore: (index: number) => void;
}> = ({ history, currentIndex, onRestore }) => {
  return (
    <div className="version-history-panel glass-card">
      <div className="panel-header">
        <ClockIcon />
        <h3>История изменений</h3>
      </div>

      <div className="history-timeline">
        {history.map((snapshot, index) => (
          <motion.button
            key={snapshot.id}
            className={cn('history-item', {
              'history-item--current': index === currentIndex,
            })}
            onClick={() => onRestore(index)}
            whileHover={{ x: 4 }}
          >
            <div className="history-timestamp">
              {formatRelativeTime(snapshot.timestamp)}
            </div>
            <div className="history-description">
              {snapshot.description}
            </div>
            {index === currentIndex && (
              <CheckCircleIcon className="history-current-indicator" />
            )}
          </motion.button>
        ))}
      </div>
    </div>
  );
};
```

---

## 🎨 Template System

Библиотека готовых шаблонов и паттернов.

```typescript
interface QuestTemplate {
  id: string;
  name: string;
  description: string;
  category: 'educational' | 'emotional' | 'story' | 'mixed';
  difficulty: 1 | 2 | 3 | 4 | 5;
  estimatedTime: number;  // minutes
  thumbnail?: string;

  // Graph structure
  nodes: Partial<QuestNode>[];
  edges: Partial<QuestEdge>[];

  // Placeholders for customization
  placeholders: {
    [key: string]: {
      type: 'text' | 'number' | 'image' | 'choice';
      label: string;
      default?: any;
    };
  };

  // Analytics
  usageCount: number;
  rating: number;
  author: string;
}

// Template Library
const builtInTemplates: QuestTemplate[] = [
  {
    id: 'linear-story-5',
    name: 'Линейная История (5 нод)',
    description: 'Простая последовательная история для начинающих',
    category: 'story',
    difficulty: 1,
    estimatedTime: 15,
    nodes: [
      { type: 'start', data: { title: 'Начало' } },
      { type: 'story', data: { title: 'Глава 1' } },
      { type: 'challenge', data: { title: 'Испытание' } },
      { type: 'reveal', data: { title: 'Открытие' } },
      { type: 'end', data: { title: 'Финал' } },
    ],
    edges: [
      { source: '0', target: '1', type: 'sequence' },
      { source: '1', target: '2', type: 'sequence' },
      { source: '2', target: '3', type: 'sequence' },
      { source: '3', target: '4', type: 'sequence' },
    ],
    placeholders: {
      story_theme: {
        type: 'text',
        label: 'Тема истории',
        default: 'Приключение',
      },
      challenge_type: {
        type: 'choice',
        label: 'Тип испытания',
        default: 'math',
      },
    },
    usageCount: 127,
    rating: 4.8,
    author: 'InnerWorld Team',
  },

  {
    id: 'branching-choice',
    name: 'Развилка с Выбором',
    description: 'История с альтернативными путями',
    category: 'story',
    difficulty: 3,
    estimatedTime: 25,
    nodes: [
      { type: 'start', data: { title: 'Начало' } },
      { type: 'story', data: { title: 'Ситуация' } },
      { type: 'choice', data: { title: 'Выбор' } },
      { type: 'story', data: { title: 'Путь A' } },
      { type: 'story', data: { title: 'Путь B' } },
      { type: 'end', data: { title: 'Финал A' } },
      { type: 'end', data: { title: 'Финал B' } },
    ],
    edges: [
      { source: '0', target: '1', type: 'sequence' },
      { source: '1', target: '2', type: 'sequence' },
      { source: '2', target: '3', type: 'conditional', data: { label: 'Вариант A' } },
      { source: '2', target: '4', type: 'conditional', data: { label: 'Вариант B' } },
      { source: '3', target: '5', type: 'sequence' },
      { source: '4', target: '6', type: 'sequence' },
    ],
    placeholders: {
      choice_prompt: {
        type: 'text',
        label: 'Вопрос для выбора',
      },
    },
    usageCount: 89,
    rating: 4.6,
    author: 'InnerWorld Team',
  },

  // ... more templates
];

// Template Palette Component
export const TemplatePalette: React.FC<{
  onSelectTemplate: (template: QuestTemplate) => void;
}> = ({ onSelectTemplate }) => {
  const [category, setCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredTemplates = useMemo(() => {
    let templates = builtInTemplates;

    if (category !== 'all') {
      templates = templates.filter(t => t.category === category);
    }

    if (searchQuery) {
      const fuse = new Fuse(templates, {
        keys: ['name', 'description'],
        threshold: 0.4,
      });
      templates = fuse.search(searchQuery).map(r => r.item);
    }

    return templates;
  }, [category, searchQuery]);

  return (
    <div className="template-palette glass-card">
      {/* Header */}
      <div className="palette-header">
        <h3>Шаблоны квестов</h3>
        <input
          type="text"
          placeholder="Поиск..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="palette-search"
        />
      </div>

      {/* Category Tabs */}
      <div className="palette-categories">
        {['all', 'educational', 'emotional', 'story', 'mixed'].map(cat => (
          <button
            key={cat}
            className={cn('category-tab', { active: category === cat })}
            onClick={() => setCategory(cat)}
          >
            {categoryLabels[cat]}
          </button>
        ))}
      </div>

      {/* Template Grid */}
      <div className="template-grid">
        {filteredTemplates.map(template => (
          <TemplateCard
            key={template.id}
            template={template}
            onClick={() => onSelectTemplate(template)}
          />
        ))}
      </div>
    </div>
  );
};

// Apply template to canvas
const applyTemplate = (template: QuestTemplate, customizations?: any) => {
  // Create nodes from template
  const newNodes = template.nodes.map((nodeTemplate, index) => ({
    ...nodeTemplate,
    id: nanoid(),
    position: {
      x: index * 250,
      y: Math.floor(index / 3) * 200,
    },
    data: {
      ...nodeTemplate.data,
      // Apply customizations
      ...(customizations?.[index] || {}),
    },
  }));

  // Create edges
  const newEdges = template.edges.map(edgeTemplate => ({
    ...edgeTemplate,
    id: nanoid(),
    source: newNodes[parseInt(edgeTemplate.source!)].id,
    target: newNodes[parseInt(edgeTemplate.target!)].id,
  }));

  // Add to canvas
  addNodes(newNodes);
  addEdges(newEdges);

  // Auto-layout
  applyLayout('hierarchical');

  // Fit view
  fitView({ padding: 50, duration: 500 });
};
```

---

## ⚡ Performance Optimizations

```typescript
// 1. Virtualization (only render visible nodes)
const useVirtualization = () => {
  const [visibleNodes, setVisibleNodes] = useState<Set<string>>(new Set());

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          const nodeId = entry.target.getAttribute('data-node-id')!;
          if (entry.isIntersecting) {
            setVisibleNodes(prev => new Set([...prev, nodeId]));
          } else {
            setVisibleNodes(prev => {
              const next = new Set(prev);
              next.delete(nodeId);
              return next;
            });
          }
        });
      },
      { rootMargin: '50px' }  // Load 50px before entering viewport
    );

    // Observe all nodes
    nodeElements.forEach(el => observer.observe(el));

    return () => observer.disconnect();
  }, [nodes]);

  return visibleNodes;
};

// 2. Throttle expensive operations
const useThrottledViewport = () => {
  const [viewport, setViewport] = useState(initialViewport);

  const throttledSetViewport = useMemo(
    () => throttle((newViewport: Viewport) => {
      setViewport(newViewport);
    }, 16),  // ~60fps
    []
  );

  return [viewport, throttledSetViewport] as const;
};

// 3. Memoize expensive computations
const useMemoizedGraph = (nodes: QuestNode[], edges: QuestEdge[]) => {
  const adjacencyList = useMemo(() => {
    const list = new Map<string, string[]>();
    edges.forEach(edge => {
      if (!list.has(edge.source)) list.set(edge.source, []);
      list.get(edge.source)!.push(edge.target);
    });
    return list;
  }, [edges]);

  const nodesByType = useMemo(() => {
    const byType = new Map<NodeType, QuestNode[]>();
    nodes.forEach(node => {
      if (!byType.has(node.type)) byType.set(node.type, []);
      byType.get(node.type)!.push(node);
    });
    return byType;
  }, [nodes]);

  return { adjacencyList, nodesByType };
};

// 4. Debounce auto-save
const useAutoSave = (graphData: { nodes: QuestNode[]; edges: QuestEdge[] }) => {
  const debouncedSave = useMemo(
    () => debounce(async (data) => {
      await saveQuestDraft(data);
      showToast('Изменения сохранены', 'success');
    }, 2000),
    []
  );

  useEffect(() => {
    debouncedSave(graphData);
  }, [graphData, debouncedSave]);
};
```

---

## 📱 Responsive Design

```typescript
// Mobile-optimized controls
const useMobileGestures = () => {
  const isMobile = useMediaQuery('(max-width: 768px)');

  if (!isMobile) return null;

  return {
    // Touch pan (single finger)
    onTouchMove: (event: TouchEvent) => {
      if (event.touches.length === 1) {
        const touch = event.touches[0];
        panCanvas(touch.clientX, touch.clientY);
      }
    },

    // Pinch zoom (two fingers)
    onPinch: usePinchGesture({
      onPinch: ({ offset: [scale] }) => {
        zoomCanvas(scale);
      },
    }),

    // Double-tap to zoom
    onDoubleTap: (event: TouchEvent) => {
      const touch = event.touches[0];
      zoomToPoint(touch.clientX, touch.clientY, 1.5);
    },
  };
};

// Mobile-optimized UI
const MobileControls: React.FC = () => {
  return (
    <div className="mobile-controls">
      {/* Floating Action Button */}
      <FAB
        icon="plus"
        onClick={() => openNodePalette()}
        position="bottom-right"
      />

      {/* Compact Toolbar */}
      <div className="mobile-toolbar glass-card">
        <IconButton icon="undo" onClick={undo} />
        <IconButton icon="redo" onClick={redo} />
        <IconButton icon="search" onClick={openSearch} />
        <IconButton icon="layout" onClick={autoLayout} />
      </div>

      {/* Gesture Hints */}
      <AnimatePresence>
        {showHints && (
          <motion.div
            className="gesture-hints glass-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
          >
            <p>👆 Один палец - перемещение</p>
            <p>🤏 Два пальца - масштаб</p>
            <p>👆👆 Двойное касание - увеличить</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
```

---

## 🧪 Validation System

```typescript
interface ValidationRule {
  id: string;
  name: string;
  description: string;
  severity: 'error' | 'warning' | 'info';
  check: (graph: { nodes: QuestNode[]; edges: QuestEdge[] }) => ValidationIssue[];
}

const validationRules: ValidationRule[] = [
  {
    id: 'has-start',
    name: 'Есть стартовая нода',
    description: 'Квест должен иметь ровно одну стартовую ноду',
    severity: 'error',
    check: ({ nodes }) => {
      const startNodes = nodes.filter(n => n.type === 'start');
      if (startNodes.length === 0) {
        return [{
          ruleId: 'has-start',
          message: 'Нет стартовой ноды',
          nodes: [],
        }];
      }
      if (startNodes.length > 1) {
        return [{
          ruleId: 'has-start',
          message: 'Больше одной стартовой ноды',
          nodes: startNodes.map(n => n.id),
        }];
      }
      return [];
    },
  },

  {
    id: 'has-end',
    name: 'Есть финальная нода',
    description: 'Квест должен иметь хотя бы одну финальную ноду',
    severity: 'error',
    check: ({ nodes }) => {
      const endNodes = nodes.filter(n => n.type === 'end');
      if (endNodes.length === 0) {
        return [{
          ruleId: 'has-end',
          message: 'Нет финальной ноды',
          nodes: [],
        }];
      }
      return [];
    },
  },

  {
    id: 'no-orphans',
    name: 'Нет изолированных нод',
    description: 'Все ноды должны быть связаны с графом',
    severity: 'warning',
    check: ({ nodes, edges }) => {
      const connectedNodes = new Set<string>();
      edges.forEach(edge => {
        connectedNodes.add(edge.source);
        connectedNodes.add(edge.target);
      });

      const orphans = nodes.filter(
        n => !connectedNodes.has(n.id) && n.type !== 'start'
      );

      if (orphans.length > 0) {
        return [{
          ruleId: 'no-orphans',
          message: `Найдено изолированных нод: ${orphans.length}`,
          nodes: orphans.map(n => n.id),
        }];
      }
      return [];
    },
  },

  {
    id: 'reachable-end',
    name: 'Финал достижим',
    description: 'Из старта должен быть путь до финала',
    severity: 'error',
    check: ({ nodes, edges }) => {
      const startNode = nodes.find(n => n.type === 'start');
      const endNodes = nodes.filter(n => n.type === 'end');

      if (!startNode || endNodes.length === 0) return [];

      const reachable = getReachableNodes(startNode.id, edges);
      const unreachableEnds = endNodes.filter(
        n => !reachable.has(n.id)
      );

      if (unreachableEnds.length > 0) {
        return [{
          ruleId: 'reachable-end',
          message: 'Некоторые финалы недостижимы',
          nodes: unreachableEnds.map(n => n.id),
        }];
      }
      return [];
    },
  },

  {
    id: 'choice-has-options',
    name: 'Развилка имеет варианты',
    description: 'Нода с выбором должна иметь минимум 2 исходящих связи',
    severity: 'error',
    check: ({ nodes, edges }) => {
      const choiceNodes = nodes.filter(n => n.type === 'choice');
      const issues: ValidationIssue[] = [];

      choiceNodes.forEach(node => {
        const outgoingEdges = edges.filter(e => e.source === node.id);
        if (outgoingEdges.length < 2) {
          issues.push({
            ruleId: 'choice-has-options',
            message: 'Развилка должна иметь минимум 2 варианта',
            nodes: [node.id],
          });
        }
      });

      return issues;
    },
  },

  // ... more rules
];

// Validation Panel
export const ValidationPanel: React.FC<{
  graph: { nodes: QuestNode[]; edges: QuestEdge[] };
}> = ({ graph }) => {
  const issues = useMemo(() => {
    const allIssues: Array<ValidationIssue & { rule: ValidationRule }> = [];

    validationRules.forEach(rule => {
      const ruleIssues = rule.check(graph);
      ruleIssues.forEach(issue => {
        allIssues.push({ ...issue, rule });
      });
    });

    return allIssues;
  }, [graph]);

  const errorCount = issues.filter(i => i.rule.severity === 'error').length;
  const warningCount = issues.filter(i => i.rule.severity === 'warning').length;

  return (
    <div className="validation-panel glass-card">
      <div className="panel-header">
        <AlertTriangleIcon />
        <h3>Проверка квеста</h3>
        {errorCount === 0 && warningCount === 0 && (
          <Badge variant="success">✓ Всё в порядке</Badge>
        )}
      </div>

      {/* Summary */}
      <div className="validation-summary">
        {errorCount > 0 && (
          <div className="summary-item error">
            <XCircleIcon />
            <span>{errorCount} ошибок</span>
          </div>
        )}
        {warningCount > 0 && (
          <div className="summary-item warning">
            <AlertCircleIcon />
            <span>{warningCount} предупреждений</span>
          </div>
        )}
      </div>

      {/* Issues List */}
      {issues.length > 0 && (
        <div className="validation-issues">
          {issues.map((issue, index) => (
            <ValidationIssueItem
              key={`${issue.ruleId}-${index}`}
              issue={issue}
              onFocus={() => focusNodes(issue.nodes)}
            />
          ))}
        </div>
      )}
    </div>
  );
};
```

---

## 🎓 Onboarding & Help

```typescript
// Interactive Tutorial
const tutorialSteps: TutorialStep[] = [
  {
    id: 'welcome',
    title: 'Добро пожаловать в Quest Builder!',
    content: 'Давайте создадим ваш первый квест за 2 минуты',
    target: null,
    position: 'center',
  },
  {
    id: 'add-node',
    title: 'Добавьте первую ноду',
    content: 'Нажмите на палитру и выберите "Начало"',
    target: '.node-palette',
    position: 'right',
    highlightTarget: true,
  },
  {
    id: 'connect-nodes',
    title: 'Соедините ноды',
    content: 'Потяните от точки справа к следующей ноде',
    target: '.node-handle-source',
    position: 'top',
  },
  {
    id: 'edit-content',
    title: 'Заполните содержание',
    content: 'Двойной клик на ноду откроет редактор',
    target: '.selected-node',
    position: 'left',
  },
  {
    id: 'preview',
    title: 'Протестируйте квест',
    content: 'Нажмите "Предпросмотр" чтобы пройти квест',
    target: '.preview-button',
    position: 'bottom',
  },
];

export const InteractiveTutorial: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isActive, setIsActive] = useState(false);

  const step = tutorialSteps[currentStep];

  if (!isActive) return null;

  return (
    <>
      {/* Overlay */}
      <div className="tutorial-overlay" />

      {/* Spotlight on target */}
      {step.target && (
        <motion.div
          className="tutorial-spotlight"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          style={{
            // Position around target element
            ...getSpotlightPosition(step.target),
          }}
        />
      )}

      {/* Tooltip */}
      <motion.div
        className="tutorial-tooltip glass-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          // Position relative to target
          ...getTooltipPosition(step.target, step.position),
        }}
      >
        <div className="tooltip-header">
          <span className="step-counter">
            {currentStep + 1} / {tutorialSteps.length}
          </span>
          <h4>{step.title}</h4>
        </div>

        <p>{step.content}</p>

        <div className="tooltip-actions">
          {currentStep > 0 && (
            <Button variant="ghost" onClick={() => setCurrentStep(currentStep - 1)}>
              Назад
            </Button>
          )}

          {currentStep < tutorialSteps.length - 1 ? (
            <Button onClick={() => setCurrentStep(currentStep + 1)}>
              Далее
            </Button>
          ) : (
            <Button onClick={() => setIsActive(false)}>
              Завершить
            </Button>
          )}

          <button
            className="skip-button"
            onClick={() => setIsActive(false)}
          >
            Пропустить
          </button>
        </div>
      </motion.div>
    </>
  );
};
```

---

## 📊 Implementation Roadmap

### Week 1-2: Core Infrastructure
- [ ] React Flow setup + Zustand store
- [ ] Basic node/edge components
- [ ] Infinite canvas with pan/zoom
- [ ] Node palette (drag-and-drop)

### Week 3: Navigation Features
- [ ] MiniMap component
- [ ] Search panel with fuzzy search
- [ ] Zoom controls + fit view
- [ ] Breadcrumb trail

### Week 4: Advanced Interactions
- [ ] Multi-select (lasso + keyboard)
- [ ] Context menus
- [ ] Undo/redo system
- [ ] Keyboard shortcuts

### Week 5: Layout & Organization
- [ ] Auto-layout algorithms (hierarchical, radial, force)
- [ ] Group nodes
- [ ] Alignment tools
- [ ] Grid snapping

### Week 6: Content Editing
- [ ] Properties panel
- [ ] Node editors (per type)
- [ ] Edge conditions editor
- [ ] Rich text support

### Week 7: Validation & Quality
- [ ] Validation system (10+ rules)
- [ ] Validation panel UI
- [ ] Auto-fix suggestions
- [ ] Structure outline

### Week 8: Templates & Productivity
- [ ] Template library (15+ templates)
- [ ] Template customization wizard
- [ ] Community templates (optional)
- [ ] Export/import YAML

### Week 9: Performance & Polish
- [ ] Virtualization
- [ ] Debouncing/throttling
- [ ] Auto-save
- [ ] Loading states

### Week 10: Collaboration (Optional)
- [ ] WebSocket integration
- [ ] Multi-user cursors
- [ ] Change broadcasting
- [ ] Conflict resolution

### Week 11: Mobile Optimization
- [ ] Touch gestures
- [ ] Responsive layout
- [ ] Mobile-optimized controls
- [ ] Gesture hints

### Week 12: Testing & Documentation
- [ ] Unit tests (Jest)
- [ ] E2E tests (Playwright)
- [ ] Interactive tutorial
- [ ] Help documentation

---

## 🎯 Success Metrics

- **Performance**: 60fps at 100+ nodes
- **Usability**: New user creates first quest in <10 minutes
- **Reliability**: <1% data loss, auto-save every 30s
- **Accessibility**: WCAG 2.1 AA compliance
- **Mobile**: Full functionality on tablets

---

**Дата создания:** 2025-11-09
**Версия:** 1.0
**Статус:** 📋 Готово к Review
