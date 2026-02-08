import React, { useState, useEffect } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  useNodesState, 
  useEdgesState, 
  MarkerType 
} from 'reactflow';
import io from 'socket.io-client';
import { Play, Activity, Terminal } from 'lucide-react'; // Добавили Terminal, чтобы не было ошибок
import 'reactflow/dist/style.css';
import './App.css';
import AgentNode from './AgentNode';

const nodeTypes = { agent: AgentNode }; 
const socket = io('http://localhost:8000'); 

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

  const addLog = (message) => {
    setLogs((prev) => [`[${new Date().toLocaleTimeString()}] ${message}`, ...prev]);
  };

  // Логика Socket.io (как в твоей старой версии)
  useEffect(() => {
    socket.on('graph_update', (event) => {
      console.log("Received event:", event);

      if (event.type === 'AGENT_FOUND') {
        const { id, role, label } = event.data;
        let bgColor = '#10B981'; 
        if (role === 'Supplier') bgColor = '#F59E0B'; 
        if (role === 'Logistics') bgColor = '#3B82F6'; 
        if (role === 'Registry') bgColor = '#EC4899'; 

        const newNode = {
          id: id,
          type: 'agent', // Используем твой красивый AgentNode
          data: { label: label, role: role, status: 'Active' },
          position: { 
            x: 400 + (Math.random() - 0.5) * 500, 
            y: 300 + (Math.random() - 0.5) * 400 
          },
        };
        setNodes((nds) => nds.concat(newNode));
        addLog(`Found agent: ${label} (${role})`);
      }

      if (event.type === 'NEGOTIATION_START') {
        const { from, to } = event;
        const newEdge = {
          id: `e-${from}-${to}`,
          source: from,
          target: to,
          animated: true,
          style: { stroke: '#00ffff', strokeWidth: 2 },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#00ffff' },
        };
        setEdges((eds) => eds.concat(newEdge));
        addLog(`Negotiation started: ${from} <-> ${to}`);
      }

      if (event.type === 'DEAL_CLOSED') {
        const { edgeId, price } = event;
        setEdges((eds) =>
          eds.map((edge) => {
            if (edge.id === edgeId) {
              return {
                ...edge,
                animated: false,
                style: { stroke: '#10B981', strokeWidth: 4 },
                label: `Confirmed: $${price}` 
              };
            }
            return edge;
          })
        );
        addLog(`✅ Deal confirmed for connection ${edgeId}`);
      }

      if (event.type === 'LOG') {
        addLog(`🧠 ${event.message}`);
      }
    });

    return () => { socket.off('graph_update'); };
  }, [setNodes, setEdges]);

  // Твоя проверенная функция симуляции (Шаг 1 -> Шаг 2 -> Шаг 3)
  const handleExecute = async () => {
    if (!intent) return;
    setIsProcessing(true);
    setNodes(initialNodes);
    setEdges([]);

    // --- ШАГ 1: Registry ---
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
      }));
    }, 1000);

    // --- ШАГ 2: Supplier ---
    const supplierId = 'supp_1';
    setTimeout(() => {
      setNodes((nds) => nds.map(n => n.id === registryId ? { ...n, data: { ...n.data, status: 'Match found!' }} : n));
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

    // --- ШАГ 3: Negotiation ---
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

    // --- ШАГ 4: Deal ---
    setTimeout(() => {
      setNodes((nds) => nds.map(n => n.id === supplierId ? { ...n, data: { ...n.data, status: 'Contract Signed ✅' }} : n));
      setEdges((eds) => eds.map(e => e.id === 'e-org-supp' ? { ...e, animated: false, label: 'Deal: $12,400', style: { stroke: '#10B981', strokeWidth: 4 }} : e));
      setIsProcessing(false);
    }, 8000);
  };

  return (
    <div className="app-container">
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

      <div style={{ width: '100%', height: '100vh' }}>
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
      
      {/* Список логов внизу для контроля */}
      <div className="logs-overlay" style={{ position: 'absolute', bottom: 20, left: 20, pointerEvents: 'none' }}>
        {logs.slice(0, 3).map((log, i) => (
          <div key={i} style={{ color: '#888', fontSize: '12px', background: 'rgba(0,0,0,0.5)', padding: '2px 8px', borderRadius: '4px' }}>
            <Terminal size={10} style={{ marginRight: 5 }} /> {log}
          </div>
        ))}
      </div>
    </div>
  );
}