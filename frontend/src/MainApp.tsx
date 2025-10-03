import React, { useState } from "react";
import axios from "axios";
import GlassCard from "./components/GlassCard.tsx";
import { useDropzone } from "react-dropzone";

const API_BASE = "http://localhost:8000"; // Change if backend runs elsewhere

function App() {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [dbStatus, setDbStatus] = useState<string | null>(null);
  const [ocrLang, setOcrLang] = useState("eng");
  const [chunkSize, setChunkSize] = useState(500);
  const [chunkOverlap, setChunkOverlap] = useState(50);
  const [embeddingModel, setEmbeddingModel] = useState("sentence-transformers/all-MiniLM-L6-v2");
  const [jsonPreview, setJsonPreview] = useState<any>(null);
  const [llmModel, setLlmModel] = useState("qwen3:1.7b"); // Default LLM model
  const [llmInstruction, setLlmInstruction] = useState("Answer concisely"); // Default instruction template;
  const [prompt, setPrompt] = useState("");
  const [chat, setChat] = useState<{ user: string; bot: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [buildStatus, setBuildStatus] = useState<'idle' | 'building' | 'success' | 'error'>('idle');
  const [buildError, setBuildError] = useState<string>('');
  const [queryHistory, setQueryHistory] = useState<Array<{question: string, answer: string, timestamp: Date}>>([]);


  const downloadDB = async () => {
  try {
    const res = await axios.get(`${API_BASE}/download_db/`, {
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "vector_db.zip");
    document.body.appendChild(link);
    link.click();
  } catch (error) {
    alert("Failed to download database");
  }
};


  const uploadJsonFile = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await axios.post(
      `${API_BASE}/build_db/?chunk_size=${chunkSize}&chunk_overlap=${chunkOverlap}&embedding_model=${embeddingModel}`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    alert("✅ JSON uploaded and processed! " + res.data.num_chunks + " chunks created.");
    setDbStatus("Database built from JSON! " + res.data.num_chunks + " chunks.");
  } catch (error) {
    alert("❌ Failed to upload JSON file.");
    setDbStatus("Error uploading JSON file.");
  }
};
  const handleRecommendChunkSettings = async () => {
  if (files.length === 0) return;

  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  try {
    const res = await axios.post(`${API_BASE}/recommend_chunk_settings/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    setChunkSize(res.data.recommended_chunk_size);
    setChunkOverlap(res.data.recommended_chunk_overlap);

    alert(
      `✅ Recommended settings applied!\n\n📦 File size: ${res.data.total_file_size_kb} KB\n🔹 Chunk Size: ${res.data.recommended_chunk_size}\n🔸 Overlap: ${res.data.recommended_chunk_overlap}`
    );
  } catch (error) {
    alert("❌ Failed to fetch recommended chunk settings.");
  }
};

  // File upload
  const onDrop = (acceptedFiles: File[]) => setFiles(acceptedFiles);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
      accept: {
    "application/pdf": [".pdf"],
    "text/csv": [".csv"],
    "application/json": [".json"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": [".pptx"],
    "text/plain": [".txt"]
  },

 
    multiple: true,
  });

  const uploadFiles = async () => {
    setUploading(true);
    setDbStatus(null);
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    formData.append("ocr_lang", ocrLang);
    try {
      setBuildStatus('building');
      const res = await axios.post(
        `${API_BASE}/build_db/?chunk_size=${chunkSize}&chunk_overlap=${chunkOverlap}&embedding_model=${embeddingModel}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setBuildStatus('success');
      setDbStatus(`✅ Database built successfully! ${res.data.num_chunks} chunks created.`);
      setJsonPreview(res.data.preview || null);
      setFiles([]);
    } catch (e: any) {
      setBuildStatus('error');
      setBuildError(e.response?.data?.detail || 'Failed to build database');
    }
    setUploading(false);
  };

  
  // Chat
  const sendPrompt = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setChat((c) => [...c, { user: prompt, bot: "..." }]);
    try {
      const res = await axios.post(`${API_BASE}/query/`, {
        prompt: `${llmInstruction}\n\n${prompt}`, // prepend instruction
        llm_model: llmModel,
        top_k: 5
      });
      setChat((c) =>
        c.slice(0, -1).concat([{ user: prompt, bot: res.data.answer.message.content }])
      );
      setQueryHistory(prev => [...prev, {
        question: prompt,
        answer: res.data.answer.message.content,
        timestamp: new Date()
      }]);
    } catch (e: any) {
      setChat((c) =>
        c.slice(0, -1).concat([{ user: prompt, bot: "Error: " + (e.response?.data?.error || e.message) }])
      );
    }
    setPrompt("");
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-zinc-900 to-zinc-800 flex flex-col items-center py-10 px-2">
      <h1 className="text-4xl md:text-5xl font-bold mb-2 tracking-tight text-white drop-shadow-lg font-futuristic">
        DIY RAG BOT
      </h1>
      <p className="text-zinc-400 mb-8 text-lg">Build Your own bot-No code</p>

      {/* File Upload */}
      <GlassCard className="w-full max-w-4xl mb-8">
        <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-6 transition-all duration-200 ${isDragActive ? "border-white bg-glass" : "border-zinc-700 bg-glass"}`}>
          <input {...getInputProps()} />
          <p className="text-center text-zinc-300">
            {isDragActive
              ? "Drop files here..."
              : "Drag & drop PDF/CSV files here, or click to select"}
          </p>
          <ul className="mt-2 text-sm text-zinc-400">
            {files.map((f) => (
              <li key={f.name}>{f.name}</li>
            ))}
          </ul>
        </div>

        {/* Additional Options */}
          <div className="flex gap-2">
    <label className="text-zinc-300 font-semibold flex-shrink-0">OCR Language:</label>
    <select
      className="flex-1 rounded-lg bg-zinc-900/80 px-2 py-1 text-white border border-zinc-700 focus:outline-none focus:ring-2 focus:ring-white/30 transition-all"
      value={ocrLang}
      onChange={(e) => setOcrLang(e.target.value)}
    >
      <option value="eng">English</option>
      <option value="hin">Hindi</option>
      <option value="tam">Tamil</option>
      <option value="tel">Telugu</option>
      <option value="ben">Bengali</option>
      <option value="guj">Gujarati</option>
      <option value="kan">Kannada</option>
      <option value="mal">Malayalam</option>
      <option value="mar">Marathi</option>
      <option value="pan">Punjabi</option>
      <option value="ori">Odia</option>
    </select>
  </div>
        <div className="mt-4 flex flex-col gap-2">
          <div className="flex gap-2">
            <label className="text-zinc-300 font-semibold flex-shrink-0">Chunk Size:</label>
            <input
              type="number"
              className="flex-1 rounded-lg bg-zinc-900/80 px-2 py-1 text-white border border-zinc-700 focus:outline-none focus:ring-2 focus:ring-white/30 transition-all"
              value={chunkSize}
              onChange={(e) => setChunkSize(parseInt(e.target.value))}
            />
          </div>
          <div className="flex gap-2">
            <label className="text-zinc-300 font-semibold flex-shrink-0">Chunk Overlap:</label>
            <input
              type="number"
              className="flex-1 rounded-lg bg-zinc-900/80 px-2 py-1 text-white border border-zinc-700 focus:outline-none focus:ring-2 focus:ring-white/30 transition-all"
              value={chunkOverlap}
              onChange={(e) => setChunkOverlap(parseInt(e.target.value))}
            />
          </div>
          <button
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-all duration-200"
            onClick={handleRecommendChunkSettings}
            disabled={files.length === 0}
          >
            Use Recommended Size
          </button>
          <div className="flex gap-2">
            <label className="text-zinc-300 font-semibold flex-shrink-0">Embedding Model:</label>
            <select
              className="flex-1 rounded-lg bg-zinc-900/80 px-2 py-1 text-white border border-zinc-700 focus:outline-none focus:ring-2 focus:ring-white/30 transition-all"
              value={embeddingModel}
              onChange={(e) => setEmbeddingModel(e.target.value)}
            >
              <option value="sentence-transformers/all-MiniLM-L6-v2">All-MiniLM-L6-v2</option>
            </select>
          </div>
          
          
        </div>

        <button
          className="mt-4 w-full py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white font-semibold transition-all duration-200 disabled:opacity-50"
          onClick={uploadFiles}
          disabled={files.length === 0 &&  uploading}
        >
          {uploading ? "Uploading..." : "Build Knowledge DB"}
          </button>
      {jsonPreview && (
        <div className="mt-4">
          <h2 className="text-lg font-semibold text-white mb-2">Preview</h2>
          <pre className="bg-zinc-900/80 p-4 rounded text-sm text-green-300 overflow-x-auto max-h-64">
            {Array.isArray(jsonPreview) ? jsonPreview.join("\n\n") : JSON.stringify(jsonPreview, null, 2)}
          </pre>
        </div>
      )}
        

        
      </GlassCard>

      {/* Chat */}
      <GlassCard className="w-full max-w-4xl flex flex-col h-[500px]">
        <div className="flex-1 overflow-y-auto px-2 py-2 space-y-4">
          {chat.length === 0 && (
            <div className="text-zinc-500 text-center mt-16">
              Ask a question after uploading your files!
            </div>
          )}
          {chat.map((msg, i) => (
            <div key={i}>
              <div className="mb-1 text-zinc-300 font-semibold">You:</div>
              <div className="mb-2 bg-white/5 rounded-lg px-3 py-2">{msg.user}</div>
              <div className="mb-1 text-zinc-400 font-semibold">Bot:</div>
              <div className="bg-white/10 rounded-lg px-3 py-2 animate-fade-in">{msg.bot}</div>
            </div>
          ))}
        </div>
        
        {/* Moved LLM controls into chat panel */}
        <div className="px-2 pb-2 space-y-2">
          <div className="flex gap-2">
            <label className="text-zinc-300 font-semibold flex-shrink-0">LLM Model:</label>
            <select
              className="flex-1 rounded-lg bg-zinc-900/80 px-2 py-1 text-white border border-zinc-700 focus:outline-none focus:ring-2 focus:ring-white/30 transition-all"
              value={llmModel}
              onChange={(e) => setLlmModel(e.target.value)}
            >
              <option value="qwen3:1.7b">qwen3:1.7b (1.4 GB) - Fast & efficient, good for general tasks</option>
              <option value="tinyllama:latest">tinyllama:latest (637 MB) - Ultra-fast for simple questions</option>
              <option value="mistral:7b-instruct-q4_K_M">mistral:7b-instruct-q4_K_M (4.4 GB) - Most capable, best for complex analysis</option>
              <option value="phi:latest">phi:latest (1.6 GB) - Microsoft's model, great for reasoning</option>
            </select>
          </div>
          <div className="flex gap-2">
            <label className="text-zinc-300 font-semibold flex-shrink-0">LLM Instruction:</label>
            <input
              type="text"
              className="flex-1 rounded-lg bg-zinc-900/80 px-2 py-1 text-white border border-zinc-700 focus:outline-none focus:ring-2 focus:ring-white/30 transition-all"
              value={llmInstruction}
              onChange={(e) => setLlmInstruction(e.target.value)}
              placeholder="Enter instruction for the LLM"
            />
          </div>
        </div>
        <div className="flex items-center gap-2 mt-2 px-2">
          <input
            className="flex-1 rounded-lg bg-zinc-900/80 px-4 py-2 text-white placeholder-zinc-500 border border-zinc-700 focus:outline-none focus:ring-2 focus:ring-white/30 transition-all"
            placeholder="Type your question..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendPrompt()}
            disabled={loading}
          />
          <button
            className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white font-semibold transition-all duration-200 disabled:opacity-50"
            onClick={sendPrompt}
            disabled={loading || !prompt.trim()}
          >
            {loading ? "..." : "Send"}
          </button>
        </div>
      </GlassCard>

      <footer className="mt-8 text-zinc-600 text-xs text-center">
        &copy; {new Date().getFullYear()} RAG Chatbot UI &mdash; Modern Minimalist
      </footer>
    </div>
  );
}

export default App;
