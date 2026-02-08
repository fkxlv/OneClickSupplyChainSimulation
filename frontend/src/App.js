import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  useNodesState, 
  useEdgesState, 
  MarkerType 
} from 'reactflow';
import io from 'socket.io-client';
import { Play, Activity, Terminal, Database, Truck, Factory, User } from 'lucide-react';
import 'reactflow/dist/style.css';
import './App.css';
import AgentNode from './AgentNode';

const nodeTypes = { agent: AgentNode }; // Регистрируем тип узла
// Подключение к бэкенду (Python/FastAPI)
const socket = io('http://localhost:8000'); 

// Начальный узел - это наш Orchestrator (Закупщик)
const initialNodes = [
  { 
    id: 'orchestrator', 
    type: 'input', 
    data: { label: '🤖 Orchestrator' }, 
    position: { x: 400, y: 300 },
    style: { background: '#7C3AED', color: 'white', border: '1px solid #8B5CF6', width: 150 }
  }
];

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [intent, setIntent] = useState('');
  const [logs, setLogs] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);

  // Функция добавления логов
  const addLog = (message) => {
    setLogs((prev) => [`[${new Date().toLocaleTimeString()}] ${message}`, ...prev]);
  };

  // Слушаем события от бэкенда через Socket.io
  useEffect(() => {
    socket.on('graph_update', (event) => {
      console.log("Received event:", event);

      // 1. НАЙДЕН НОВЫЙ АГЕНТ (Добавляем узел)
      if (event.type === 'AGENT_FOUND') {
        const { id, role, label } = event.data;
        
        // Выбираем иконку/цвет по роли
        let bgColor = '#10B981'; // Green for generic
        if (role === 'Supplier') bgColor = '#F59E0B'; // Orange
        if (role === 'Logistics') bgColor = '#3B82F6'; // Blue
        if (role === 'Registry') bgColor = '#EC4899'; // Pink

        const newNode = {
          id: id,
          data: { label: label },
          // Случайная позиция вокруг центра (для демо)
          position: { 
            x: 400 + (Math.random() - 0.5) * 500, 
            y: 300 + (Math.random() - 0.5) * 400 
          },
          style: { background: bgColor, color: 'white', border: 'none', borderRadius: '8px' }
        };
        setNodes((nds) => nds.concat(newNode));
        addLog(`Found agent: ${label} (${role})`);
      }

      // 2. ПЕРЕГОВОРЫ (Рисуем анимированную линию)
      if (event.type === 'NEGOTIATION_START') {
        const { from, to } = event;
        const newEdge = {
          id: `e-${from}-${to}`,
          source: from,
          target: to,
          animated: true, // Включает анимацию "потока данных"
          style: { stroke: '#00ffff', strokeWidth: 2 },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#00ffff' },
        };
        setEdges((eds) => eds.concat(newEdge));
        addLog(`Negotiation started: ${from} <-> ${to}`);
      }

      // 3. СДЕЛКА ЗАКРЫТА (Линия становится зеленой и статической)
      if (event.type === 'DEAL_CLOSED') {
        const { edgeId, price } = event;
        setEdges((eds) =>
          eds.map((edge) => {
            if (edge.id === edgeId) {
              return {
                ...edge,
                animated: false,
                style: { stroke: '#10B981', strokeWidth: 4 }, // Жирная зеленая линия
                label: `Confirmed: $${price}` // Показываем цену на линии
              };
            }
            return edge;
          })
        );
        addLog(`✅ Deal confirmed for connection ${edgeId}`);
      }

      // 4. ПРОСТО ЛОГ МЫСЛЕЙ (Gemini Reasoning)
      if (event.type === 'LOG') {
        addLog(`🧠 ${event.message}`);
      }
    });

    return () => {
      socket.off('graph_update');
    };
  }, [setNodes, setEdges]);

  // Нажатие кнопки "One Click"
 const handleExecute = async () => {
  if (!intent) return;
  setIsProcessing(true);
  
  // 1. Очистка старого графа (оставляем только Orchestrator)
  setNodes(initialNodes);
  setEdges([]);

  // --- ШАГ 1: Обращение к Реестру (Registry) ---
  const registryId = 'reg_1';
  setTimeout(() => {
    setNodes((nds) => nds.concat({
      id: registryId,
      type: 'agent',
      data: { label: 'Global Registry', role: 'Registry', status: 'Searching database...' },
      position: { x: 400, y: 100 },
    }));
    
    setEdges((eds) => eds.concat({
      id: 'e-org-reg',
      source: 'orchestrator',
      target: registryId,
      label: 'Requesting Suppliers',
      animated: true,
      style: { stroke: '#EC4899' },
      labelStyle: { fill: '#EC4899', fontSize: 10 }
    }));
  }, 1000);

  // --- ШАГ 2: Реестр выдает Поставщика ---
  const supplierId = 'supp_1';
  setTimeout(() => {
    // Обновляем статус реестра
    setNodes((nds) => nds.map(n => n.id === registryId ? { ...n, data: { ...n.data, status: 'Match found!' }} : n));
    
    // Появляется поставщик
    setNodes((nds) => nds.concat({
      id: supplierId,
      type: 'agent',
      data: { label: 'Steel Corp (Asia)', role: 'Supplier', status: 'Waiting...' },
      position: { x: 700, y: 300 },
    }));

    setEdges((eds) => eds.concat({
      id: 'e-reg-supp',
      source: registryId,
      target: supplierId,
      label: 'Agent Metadata',
      animated: true,
      style: { stroke: '#F59E0B' },
    }));
  }, 3000);

  // --- ШАГ 3: Переговоры (Оркестратор <-> Поставщик) ---
  setTimeout(() => {
    setNodes((nds) => nds.map(n => n.id === supplierId ? { ...n, data: { ...n.data, status: 'Negotiating price...' }} : n));
    
    setEdges((eds) => eds.concat({
      id: 'e-org-supp',
      source: 'orchestrator',
      target: supplierId,
      label: 'Negotiating RFQ',
      animated: true,
      style: { stroke: '#00ffff', strokeWidth: 2 },
    }));
  }, 5000);

  // --- ШАГ 4: Завершение (Сделка) ---
  setTimeout(() => {
    setNodes((nds) => nds.map(n => n.id === supplierId ? { ...n, data: { ...n.data, status: 'Contract Signed ✅' }} : n));
    setEdges((eds) => eds.map(e => e.id === 'e-org-supp' ? { ...e, animated: false, label: 'Deal: $12,400', style: { stroke: '#10B981', strokeWidth: 4 }} : e));
    setIsProcessing(false);
  }, 8000);
};

  return (
  <div className="app-container">
      {/* HEADER & INPUT SECTION */}
      <div className="control-panel">
        <h1 className="title">
          <Activity className="icon" /> NANDA Supply Chain <span className="highlight">Orchestrator</span>
        </h1>
        <div className="input-group">
          <input
            type="text"
            placeholder="Describe your intent (e.g., 'Source 500 drone motors from Asia...')"
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            disabled={isProcessing}
          />
          <button onClick={handleExecute} disabled={isProcessing || !intent}>
            <Play size={18} /> {isProcessing ? 'Orchestrating...' : 'One Click Execute'}
          </button>
        </div>
      </div>

    {/* Холст графа */}
    <ReactFlow 
      nodes={nodes} 
      edges={edges} 
      nodeTypes={nodeTypes}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      fitView
    >
      <Background color="#222" gap={20} />
      <Controls />
    </ReactFlow>
  </div>
);
}