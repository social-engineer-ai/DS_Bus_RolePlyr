'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, RubricChatMessage, RubricDraft, CriterionSchema } from '@/lib/api';

const DEFAULT_COURSE_ID = '55555555-5555-5555-5555-555555555555';

export default function AIRubricBuilderPage() {
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<RubricChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [materialsText, setMaterialsText] = useState('');
  const [rubricDraft, setRubricDraft] = useState<RubricDraft | null>(null);
  const [sending, setSending] = useState(false);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setError(null);
      const result = await api.uploadRubricMaterial(file);
      setMaterialsText((prev) => (prev ? prev + '\n\n---\n\n' : '') + result.extracted_text);
      setUploadedFiles((prev) => [...prev, result.filename]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleSend = async () => {
    if (!input.trim() || sending) return;

    const userMessage: RubricChatMessage = { role: 'user', content: input.trim() };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');
    setSending(true);
    setError(null);

    try {
      const response = await api.rubricChat(newMessages, materialsText);
      const assistantMessage: RubricChatMessage = { role: 'assistant', content: response.reply };
      setMessages([...newMessages, assistantMessage]);
      if (response.rubric_draft) {
        setRubricDraft(response.rubric_draft);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat failed');
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSaveRubric = async () => {
    if (!rubricDraft) return;

    try {
      setSaving(true);
      setError(null);
      await api.createRubric({
        course_id: DEFAULT_COURSE_ID,
        name: rubricDraft.name,
        criteria: rubricDraft.criteria,
      });
      router.push('/instructor/rubrics');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save rubric');
    } finally {
      setSaving(false);
    }
  };

  const totalPoints = rubricDraft?.criteria.reduce((sum, c) => sum + c.max_points, 0) || 0;

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <header className="bg-indigo-600 text-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">AI Rubric Builder</h1>
            <p className="text-sm text-indigo-200">Chat with AI to design your rubric</p>
          </div>
          <nav className="flex gap-4 items-center">
            <a href="/instructor/rubrics" className="text-indigo-200 hover:text-white">Back to Rubrics</a>
            {rubricDraft && (
              <button
                onClick={handleSaveRubric}
                disabled={saving}
                className="bg-white text-indigo-600 px-4 py-2 rounded-lg font-medium hover:bg-indigo-50 disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save Rubric'}
              </button>
            )}
          </nav>
        </div>
      </header>

      {error && (
        <div className="bg-red-50 text-red-700 p-3 text-center text-sm">
          {error}
          <button onClick={() => setError(null)} className="ml-3 text-red-500 hover:text-red-700">Dismiss</button>
        </div>
      )}

      {/* Materials Upload Bar */}
      <div className="bg-white border-b px-4 py-3">
        <div className="max-w-7xl mx-auto flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="bg-gray-100 text-gray-700 px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-gray-200 cursor-pointer">
              {uploading ? 'Uploading...' : 'Upload PDF/DOCX'}
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={handleUpload}
                className="hidden"
                disabled={uploading}
              />
            </label>
            {uploadedFiles.length > 0 && (
              <div className="flex gap-1">
                {uploadedFiles.map((f, i) => (
                  <span key={i} className="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded text-xs">{f}</span>
                ))}
              </div>
            )}
          </div>
          <div className="flex-1">
            <input
              type="text"
              value={materialsText ? `${materialsText.length} chars of material loaded` : ''}
              readOnly
              placeholder="Or paste text below..."
              className="w-full text-sm text-gray-500 bg-transparent outline-none"
            />
          </div>
          <button
            onClick={() => {
              const text = prompt('Paste your materials text (learning objectives, syllabus, etc.):');
              if (text) setMaterialsText((prev) => (prev ? prev + '\n\n---\n\n' : '') + text);
            }}
            className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
          >
            Paste Text
          </button>
        </div>
      </div>

      {/* Main Content: Chat + Preview */}
      <div className="flex-1 flex max-w-7xl mx-auto w-full">
        {/* Chat Panel */}
        <div className="flex-1 flex flex-col border-r">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <p className="text-lg font-medium mb-2">Welcome to the AI Rubric Builder</p>
                <p className="text-sm">Upload materials or describe what you want to assess.</p>
                <p className="text-sm mt-1">Try: "Create a rubric for a stakeholder presentation about budget approval"</p>
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-gray-800 shadow'
                }`}>
                  <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                </div>
              </div>
            ))}
            {sending && (
              <div className="flex justify-start">
                <div className="bg-white text-gray-500 rounded-lg px-4 py-2 shadow">
                  <p className="text-sm">Thinking...</p>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input */}
          <div className="border-t bg-white p-4">
            <div className="flex gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Describe your rubric needs or refine the draft..."
                className="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                rows={2}
                disabled={sending}
              />
              <button
                onClick={handleSend}
                disabled={sending || !input.trim()}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed self-end"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        {/* Rubric Preview Panel */}
        <div className="w-96 bg-white overflow-y-auto p-4">
          <h3 className="font-semibold text-gray-800 mb-4">Rubric Preview</h3>
          {rubricDraft ? (
            <div className="space-y-3">
              <div>
                <h4 className="font-medium text-gray-900 text-lg">{rubricDraft.name}</h4>
                <p className="text-sm text-gray-500">{rubricDraft.criteria.length} criteria | {totalPoints} total points</p>
              </div>

              {rubricDraft.criteria.map((criterion: CriterionSchema, i: number) => (
                <div key={i} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <h5 className="font-medium text-gray-900 text-sm">{criterion.display_name}</h5>
                    <span className="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded text-xs font-medium">
                      {criterion.max_points} pts
                    </span>
                  </div>
                  {criterion.description && (
                    <p className="text-xs text-gray-600 mb-2">{criterion.description}</p>
                  )}
                  {criterion.scoring_guide && Object.keys(criterion.scoring_guide).length > 0 && (
                    <div className="bg-gray-50 rounded p-2">
                      <p className="text-xs font-medium text-gray-500 mb-1">Scoring Guide</p>
                      {Object.entries(criterion.scoring_guide)
                        .sort(([a], [b]) => Number(b) - Number(a))
                        .map(([score, desc]) => (
                          <div key={score} className="text-xs text-gray-600 flex gap-1">
                            <span className="font-medium w-6">{score}:</span>
                            <span>{desc}</span>
                          </div>
                        ))}
                    </div>
                  )}
                </div>
              ))}

              <button
                onClick={handleSaveRubric}
                disabled={saving}
                className="w-full bg-indigo-600 text-white py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 mt-4"
              >
                {saving ? 'Saving...' : 'Save Rubric'}
              </button>
            </div>
          ) : (
            <div className="text-center text-gray-400 mt-8">
              <p className="text-sm">No rubric draft yet.</p>
              <p className="text-xs mt-1">Start chatting to generate one.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
