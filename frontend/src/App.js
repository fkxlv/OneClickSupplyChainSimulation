import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  useNodesState, 
  useEdgesState, 
  MarkerType 
} from 'reactflow';
import io from 'socket.io-client';
import { Play, Activity, Database, Box, MapPin, ClipboardList, Brain, Terminal } from 'lucide-react';
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
  
  // Состояние для данных из Gemini
  const [planData, setPlanData] = useState(null);

  const addLog = (message) => {
    setLogs((prev) => [`[${new Date().toLocaleTimeString()}] ${message}`, ...prev]);
  };

  // Вызов API Бэкенда
  const fetchPlan = async (userIntent) => {
    try {
      const response = await fetch('http://127.0.0.1:5001/planner/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          intent: userIntent, 
          request_id: `req-${Math.random().toString(36).substr(2, 9)}` 
        })
      });
      return await response.json();
    } catch (error) {
      console.error("API Error:", error);
      return null;
    }
  };

  const handleExecute = async () => {
    if (!intent) return;
    setIsProcessing(true);
    setPlanData(null); // Сброс старых данных
    setNodes(initialNodes);
    setEdges([]);
    
    addLog("🧠 Analyzing intent with Gemini AI...");

    // 1. Получаем данные от бэкенда
    const data = await fetchPlan(intent);
    
    if (!data) {
      addLog("❌ Failed to connect to Backend Server.");
      setIsProcessing(false);
      return;
    }

    setPlanData(data); // Заполняем "окошки" данными
    addLog(`✅ Plan Extracted: ${data.product} (${data.quantity} units)`);

    // --- СИМУЛЯЦИЯ ГРАФА НА ОСНОВЕ ДАННЫХ ---
    
    // Шаг 1: Registry
    const registryId = 'reg_1';
    setTimeout(() => {
      setNodes((nds) => nds.concat({
        id: registryId,
        type: 'agent',
        data: { label: 'Global Registry', role: 'Registry', status: 'Searching...' },
        position: { x: 400, y: 100 },
      }));
      setEdges((eds) => eds.concat({
        id: 'e-org-reg',
        source: 'orchestrator',
        target: registryId,
        label: 'Find Suppliers',
        animated: true,
        style: { stroke: '#EC4899' }
      }));
      addLog("🔎 Searching for suppliers in " + (data.constraints?.region || "Global Market"));
    }, 1000);

    // Шаг 2: Поставщик (на основе продукта из API)
    const supplierId = 'supp_1';
    setTimeout(() => {
      setNodes((nds) => nds.concat({
        id: supplierId,
        type: 'agent',
        data: { label: `Supplier: ${data.product}`, role: 'Supplier', status: 'Negotiating...' },
        position: { x: 700, y: 300 },
      }));
      setEdges((eds) => eds.concat({
        id: 'e-reg-supp',
        source: registryId,
        target: supplierId,
        animated: true,
        style: { stroke: '#F59E0B' }
      }));
      addLog(`🤝 Negotiating terms for ${data.quantity} units...`);
    }, 3000);

    // Шаг 3: Финализация
    setTimeout(() => {
      setEdges((eds) => eds.concat({
        id: 'e-org-supp',
        source: 'orchestrator',
        target: supplierId,
        label: `Deal Confirmed`,
        animated: false,
        style: { stroke: '#10B981', strokeWidth: 4 }
      }));
      addLog("🎯 Orchestration complete!");
      setIsProcessing(false);
    }, 5000);
  };

  return (
    <div className="app-container">
      {/* ПАНЕЛЬ УПРАВЛЕНИЯ */}
      <div className="control-panel">
        <h1 className="title">
          <Activity className="icon" /> NANDA <span className="highlight">Orchestrator</span>
        </h1>
        <div className="input-group">
          <input
            type="text"
            placeholder="What do you need to source?"
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            disabled={isProcessing}
          />
          <button onClick={handleExecute} disabled={isProcessing || !intent}>
            <Play size={18} /> {isProcessing ? 'Processing...' : 'Execute'}
          </button>
        </div>
      </div>

      <div className="main-layout">
        {/* ЛЕВАЯ ПАНЕЛЬ: ЛОГИ */}
        <div className="side-panel logs-panel">
          <h3><Terminal size={16} /> Live Logs</h3>
          <div className="log-list">
            {logs.map((log, i) => <div key={i} className="log-item">{log}</div>)}
          </div>
        </div>

        {/* ЦЕНТР: ГРАФ */}
        <div className="graph-container">
          <ReactFlow 
            nodes={nodes} 
            edges={edges} 
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
          >
            <Background color="#1a1a1a" gap={20} />
            <Controls />
          </ReactFlow>
        </div>

        {/* ПРАВАЯ ПАНЕЛЬ: ТЕ САМЫЕ ОКОШКИ */}
        <div className="side-panel data-panel">
          <h3><Brain size={18} color="#8B5CF6" /> AI Extraction</h3>
          
          <div className="info-box">
            <label><Box size={14} /> Product</label>
            <div className="value">{planData?.product || '—'}</div>
          </div>

          <div className="info-box">
            <label><Activity size={14} /> Quantity</label>
            <div className="value">{planData?.quantity || '0'}</div>
          </div>

          <div className="info-box">
            <label><MapPin size={14} /> Destination</label>
            <div className="value">{planData?.constraints?.region || 'Not set'}</div>
          </div>

          <div className="info-box checklist">
            <label><ClipboardList size={14} /> Action Plan</label>
            <ul>
              {planData?.checklist?.map((step, i) => (
                <li key={i}>{step}</li>
              )) || <li>Waiting for intent...</li>}
            </ul>
          </div>
          
          {planData?.reasoning_summary && (
            <div className="reasoning-note">
              <small>{planData.reasoning_summary}</small>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}