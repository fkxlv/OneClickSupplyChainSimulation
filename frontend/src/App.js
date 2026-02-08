import React, { useState, useCallback } from 'react';
import ReactFlow, { Background, Controls, useNodesState, useEdgesState } from 'reactflow';
import { Play, Activity, Terminal, Box } from 'lucide-react';
// УДАЛЕНО: import { io } from "socket.io-client"; 
import 'reactflow/dist/style.css';
import './App.css';
import AgentNode from './AgentNode';

const nodeTypes = { agent: AgentNode };

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [intent, setIntent] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [logs, setLogs] = useState([]);

  const addLog = (msg) => {
    setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev].slice(0, 5));
  };

  // Функция для имитации задержки (чтобы граф рос постепенно)
  const delay = (ms) => new Promise(res => setTimeout(res, ms));

  const handleExecute = async () => {
    if (!intent) return;
    setIsProcessing(true);
    setNodes([]); 
    setEdges([]);
    addLog("Запрос отправлен в Gemini Planner...");

    try {
      // 1. Создаем начальный узел (Оркестратор)
      const orchestratorId = 'node-0';
      setNodes([{
        id: orchestratorId,
        type: 'agent',
        data: { label: 'Orchestrator', role: 'CORE AI', status: 'Thinking...' },
        position: { x: 400, y: 50 },
      }]);

      // 2. HTTP POST запрос к вашему API
      const response = await fetch('http://localhost:5001/planner/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intent })
      });
      
      if (!response.ok) throw new Error("Ошибка сервера");
      
      const data = await response.json();
      addLog(`План получен: ${data.product}`);

      // 3. Анимируем появление шагов из checklist
      let lastId = orchestratorId;
      for (let i = 0; i < data.checklist.length; i++) {
        await delay(800); 
        
        const stepId = `step-${i}`;
        const newNode = {
          id: stepId,
          type: 'agent',
          data: { label: data.checklist[i], role: 'SUPPLY AGENT', status: 'Active' },
          position: { x: 400 + (i % 2 === 0 ? 150 : -150), y: 150 + (i + 1) * 150 },
        };

        const newEdge = {
          id: `e-${lastId}-${stepId}`,
          source: lastId,
          target: stepId,
          animated: true,
          style: { stroke: '#8b5cf6' }
        };

        setNodes(nds => [...nds, newNode]);
        setEdges(eds => [...eds, newEdge]);
        lastId = stepId;
        addLog(`Развернут агент: ${data.checklist[i]}`);
      }

      // Обновляем статус главного узла
      setNodes(nds => nds.map(n => n.id === 'node-0' ? 
        {...n, data: {...n.data, status: 'Готово'}} : n
      ));

    } catch (err) {
      addLog("Ошибка: Не удалось связаться с сервером");
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="app-viewport">
      <aside className="planner-side-panel">
        <h2 className="planner-header"><Box size={24} /> AI Planner</h2>
        <div className="mini-logs">
          {logs.map((log, i) => (
            <div key={i} className="log-entry"><Terminal size={10} /> {log}</div>
          ))}
        </div>
      </aside>

      <main className="main-content">
        <header className="top-bar">
          <div className="input-wrapper">
            <input 
              value={intent} 
              onChange={(e) => setIntent(e.target.value)}
              placeholder="Введите задачу (например: Закупить 50 дронов)..." 
              disabled={isProcessing}
            />
            <button onClick={handleExecute} disabled={isProcessing}>
              {isProcessing ? <Activity className="spin" size={18} /> : <Play size={18} />}
              <span>Запустить</span>
            </button>
          </div>
        </header>

        <section className="graph-frame">
          <ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} fitView>
            <Background color="#1a1a2e" gap={20} />
            <Controls />
          </ReactFlow>
        </section>
      </main>
    </div>
  );
}