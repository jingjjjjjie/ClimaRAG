import { useState, useEffect } from 'react';
import { useImmer } from 'use-immer';
import api from '@/api';
import ChatMessages from '@/components/ChatMessages';
import ChatInput from '@/components/ChatInput';

function Chatbot() {
  const [chatId, setChatId] = useState(null);
  const [messages, setMessages] = useImmer([]);
  const [newMessage, setNewMessage] = useState('');
  const [isPageVisible, setIsPageVisible] = useState(true);

  const isLoading = messages.length && messages[messages.length - 1].loading;

  useEffect(() => {
    function handleVisibilityChange() {
      setIsPageVisible(!document.hidden);
    }

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  function streamAnswer(answer) {
    const worker = new Worker(new URL('../streamWorker.js', import.meta.url));
    const chunkSize = 1; // Adjust as needed

    worker.postMessage({ answer, chunkSize });

    worker.onmessage = function(event) {
      const { chunk, done } = event.data;

      if (!done) {
        setMessages(draft => {
          draft[draft.length - 1].content += chunk;
        });
      } else {
        setMessages(draft => {
          draft[draft.length - 1].loading = false;
        });
        worker.terminate();
      }
    };
  }

  async function submitNewMessage() {
    const trimmedMessage = newMessage.trim();
    if (!trimmedMessage || isLoading) return;

    setMessages(draft => [
      ...draft,
      { role: 'user', content: trimmedMessage },
      { role: 'assistant', content: '', sources: [], loading: true }
    ]);
    setNewMessage('');

    let chatIdOrNew = chatId;
    try {
      if (!chatId) {
        const { id } = await api.createChat();
        setChatId(id);
        chatIdOrNew = id;
      }

      const stream = await api.sendChatMessage(chatIdOrNew, trimmedMessage);
      console.log(stream);

      const answer = stream.answer;
      console.log(answer);

      streamAnswer(answer);

    } catch (err) {
      console.log(err);
      setMessages(draft => {
        draft[draft.length - 1].loading = false;
        draft[draft.length - 1].error = true;
      });
    }
  }

  return (
    <div className='relative grow flex flex-col gap-6 pt-6'>
      {messages.length === 0 && (
        <div className='mt-3 font-urbanist text-primary-blue text-xl font-light space-y-2'>
          <p>👋 Welcome!</p>
          <p>I am a chatbot focusing on the field of Climate Changes.</p>
          <p>Ask me anything about this topic and I will tell you the answer.</p>
        </div>
      )}
      <ChatMessages
        messages={messages}
        isLoading={isLoading}
      />
      <ChatInput
        newMessage={newMessage}
        isLoading={isLoading}
        setNewMessage={setNewMessage}
        submitNewMessage={submitNewMessage}
      />
    </div>
  );
}

export default Chatbot;
