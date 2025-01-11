import { useState, useEffect } from 'react';
import { useImmer } from 'use-immer';
import Chatbot from '@/components/Chatbot';
import Sidebar from '@/components/Sidebar';
import api from './api';

function App() {
  const [chatId, setChatId] = useState(() => sessionStorage.getItem('chatId') || null);
  const [messages, setMessages] = useImmer([]);
  const [conversations, setConversations] = useState([]);

  useEffect(() => {
    if (chatId) {
      sessionStorage.setItem('chatId', chatId);
    }
  }, [chatId]);

  const fetchConversations = async () => {
    try {
      const response = await api.getConversationHistory();
      setConversations(response);
    } catch (error) {
      console.error("Error fetching conversations:", error);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  const startNewChat = async () => {
    console.log("Starting a new chat...");
    sessionStorage.clear(); 
    setChatId(null);
    setMessages([]);
    await fetchConversations(); // Fetch updated conversations after starting a new chat
  };

  const fetchMessages = async (sessionId) => {
    try {
      const response = await api.getMessageHistory(sessionId);
      setChatId(sessionId);
      setMessages(response); // Set the messages for the selected chat session
    } catch (error) {
      console.error("Error fetching messages:", error);
    }
  };

  return (
    <div className="flex h-screen">
      <Sidebar startNewChat={startNewChat} conversations={conversations} fetchMessages={fetchMessages} fetchConversations={fetchConversations} />
      <div className="flex flex-col min-h-full w-full max-w-3xl mx-auto px-4">
        <header className="sticky top-0 shrink-0 z-20">
          <div className="flex flex-col h-full w-full gap-1 pt-4 pb-2">
            <h1 className="font-urbanist text-[1.65rem] font-semibold">Climate Change AI Chatbot</h1>
          </div>
        </header>
        <Chatbot
          chatId={chatId}
          setChatId={setChatId}
          messages={messages}
          setMessages={setMessages}
          startNewChat={startNewChat}
        />
      </div>
    </div>
  );
}

export default App;
