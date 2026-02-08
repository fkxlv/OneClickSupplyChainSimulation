import React, { useState } from 'react';
import ReactFlow, { 
  Background, Controls, useNodesState, useEdgesState 
} from 'reactflow';
import { Play, Activity, Box, MapPin, ClipboardList, Brain, CheckCircle } from 'lucide-react';
import 'reactflow/dist/style.css';
import './App.css';
import AgentNode from './AgentNode';

const nodeTypes = { agent: AgentNode };

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [intent, setIntent] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [planData, setPlanData] = useState(null);

  // Вызов твоего Бэкенда
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
    setPlanData(null);
    
    // Начальное состояние графа
    const initialOrchestrator = { 
      id: 'orchestrator', 
      type: 'agent', 
      data: { label: '🤖 Orchestrator', role: 'Main Intelligence', status: 'Analyzing Intent...' }, 
      position: { x: 400, y: 300 } 
    };
    setNodes([initialOrchestrator]);
    setEdges([]);

    // 1. Получаем реальный план от Gemini
    const data = await fetchPlan(intent);
    if (!data) {
      setIsProcessing(false);
      return;
    }
    setPlanData(data);

    // 2. Анимация: Registry
    setTimeout(() => {
      setNodes((nds) => nds.concat({
        id: 'reg_1',
        type: 'agent',
        data: { label: 'Global Registry', role: 'Registry', status: 'Searching Suppliers...' },
        position: { x: 400, y: 80 },
      }));
      setEdges((eds) => eds.concat({
        id: 'e1', source: 'orchestrator', target: 'reg_1', animated: true, style: { stroke: '#EC4899' }
      }));
    }, 1500);

    // 3. Анимация: Поставщик (Берем имя продукта из API)
    setTimeout(() => {
      setNodes((nds) => nds.concat({
        id: 'supp_1',
        type: 'agent',
        data: { 
          label: `${data.product} Factory`, 
          role: 'Supplier', 
          status: `Ready: ${data.quantity} units` 
        },
        position: { x: 750, y: 300 },
      }));
      setEdges((eds) => eds.concat({
        id: 'e2', source: 'reg_1', target: 'supp_1', animated: true, style: { stroke: '#F59E0B' }
      }));
    }, 3500);

    // 4. Финализация
    setTimeout(() => {
      setEdges((eds) => eds.concat({
        id: 'e3', source: 'orchestrator', target: 'supp_1', label: 'RFQ Signed', animated: false, 
        style: { stroke: '#10B981', strokeWidth: 3 }
      }));
      setIsProcessing(false);
    }, 5500);
  };

  return (
    <div className="app-viewport">
      {/* ЛЕВАЯ ПАНЕЛЬ: ПЛАНИРОВЩИК (PLANNER) */}
      <div className="planner-side-panel">
        <div className="planner-header">
          <Brain size={20} color="#8B5CF6" />
          <h2>AI Planner</h2>
        </div>

        {planData ? (
          <div className="plan-content">
            <div className="data-card">
              <div className="card-item"><Box size={16} /> <span>{planData.product}</span></div>
              <div className="card-item"><Activity size={16} /> <span>{planData.quantity} units</span></div>
              <div className="card-item"><MapPin size={16} /> <span>{planData.constraints?.region || 'Global'}</span></div>
            </div>

            <div className="checklist-section">
              <h4><ClipboardList size={16} /> Strategy Steps:</h4>
              <div className="steps-list">
                {planData.checklist?.map((step, i) => (
                  <div key={i} className="step-row">
                    <CheckCircle size={14} className="check-icon" />
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <p>Waiting for mission intent...</p>
          </div>
        )}
      </div>

      {/* ПРАВАЯ ЧАСТЬ: ИНПУТ И ГРАФ */}
      <div className="main-content">
        <div className="top-bar">
          <div className="input-wrapper">
            <input 
              value={intent}
              onChange={(e) => setIntent(e.target.value)}
              placeholder="Ex: Source 500 units of steel for Berlin..." 
              disabled={isProcessing}
            />
            <button onClick={handleExecute} disabled={isProcessing || !intent}>
              {isProcessing ? <Activity className="spin" size={18} /> : <Play size={18} />}
              <span>{isProcessing ? 'Thinking...' : 'Execute'}</span>
            </button>
          </div>
        </div>

        <div className="graph-frame">
          <ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} fitView>
            <Background color="#111" gap={20} />
            <Controls />
          </ReactFlow>
        </div>
      </div>
    </div>
  );
}