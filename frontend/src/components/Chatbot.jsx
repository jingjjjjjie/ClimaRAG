import { useState, useEffect, useRef } from 'react';
import { useImmer } from 'use-immer';
import api from '@/api';
import ChatMessages from '@/components/ChatMessages';
import ChatInput from '@/components/ChatInput';
import downArrowIcon from '@/assets/images/icons8-arrow-down-24.png';
import useAutoScroll from '@/hooks/useAutoScroll';

function Chatbot({ chatId, setChatId, messages, setMessages, startNewChat }) {
  const [newMessage, setNewMessage] = useState('');
  const [isPageVisible, setIsPageVisible] = useState(true);
  const messagesEndRef = useRef(null);
  const [showButton, setShowButton] = useState(false);
  const scrollContentRef = useAutoScroll();
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

  useEffect(() => {
    const savedChatId = sessionStorage.getItem('chatId');
    const savedMessages = sessionStorage.getItem('messages');

    if (savedChatId) {
      setChatId(savedChatId);
    }

    if (savedMessages) {
      const parsedMessages = JSON.parse(savedMessages);
      setMessages(parsedMessages);
    }
  }, [setChatId, setMessages]);

  useEffect(() => {
    if (messages.length) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  function streamAnswer(answer) {
    const worker = new Worker(new URL('../streamWorker.js', import.meta.url));
    const chunkSize = 5;

    worker.postMessage({ answer, chunkSize });

    worker.onmessage = function(event) {
      const { chunk, done } = event.data;

      if (!done) {
        setMessages(draft => {
          draft[draft.length - 1].content += chunk;
          sessionStorage.setItem('messages', JSON.stringify(draft));
        });
      } else {
        setMessages(draft => {
          draft[draft.length - 1].loading = false;
          sessionStorage.setItem('messages', JSON.stringify(draft));
        });
        worker.terminate();
      }
    };
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const isOverflowing = () => {
  const { scrollHeight, clientHeight, scrollTop } = scrollContentRef.current;
  return scrollHeight > clientHeight && scrollTop + clientHeight < scrollHeight;
};


  async function submitNewMessage(message = newMessage) {
    const trimmedMessage = message.trim();
    if (!trimmedMessage || isLoading) return;

    setMessages(draft => {
      const updatedMessages = [
        ...draft,
        { role: 'user', content: trimmedMessage },
        { role: 'assistant', content: '', sources: [], loading: true }
      ];
      sessionStorage.setItem('messages', JSON.stringify(updatedMessages));
      return updatedMessages;
    });
    setNewMessage('');

    let chatIdOrNew = chatId;
    try {
      if (!chatId) {
        const { id } = await api.createChat();
        setChatId(id);
        chatIdOrNew = id;
      }

      const stream = await api.sendChatMessage(chatIdOrNew, trimmedMessage);
      const answer = stream.answer;

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
    <div 
      className='relative grow flex flex-col gap-6 pt-6'
      onMouseEnter={() => setShowButton(true)} 
      onMouseLeave={() => setShowButton(false)} 
    >
      {messages.length === 0 && (
        <div className='mt-3 font-urbanist text-primary-blue text-xl font-light space-y-2'>
          <p>👋 Welcome!</p>
          <p>I am a chatbot focusing on the field of Climate Changes.</p>
          <p>Ask me anything about this topic and I will tell you the answer.</p>
        </div>
      )}
      <div ref={scrollContentRef} className='flex-grow overflow-y-auto max-h-[calc(100vh-200px)] hide-scrollbar'>
        <ChatMessages messages={messages} isLoading={isLoading} />
        <div ref={messagesEndRef} />
      </div>
      {showButton && isOverflowing() && (
        <button 
          onClick={scrollToBottom} 
          className='absolute left-1/2 bottom-16 transform -translate-x-1/2 p-1 bg-primary-blue rounded transition-opacity duration-300 mb-4'
        >
          <img src={downArrowIcon} alt='Jump to Down' className='h-4 w-4' />
        </button>
      )}
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
