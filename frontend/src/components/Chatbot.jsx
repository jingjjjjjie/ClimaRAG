import { useState } from 'react';
import { useImmer } from 'use-immer';
import api from '@/api';
import ChatMessages from '@/components/ChatMessages';
import ChatInput from '@/components/ChatInput';

function Chatbot() {
  const [chatId, setChatId] = useState(null);
  const [messages, setMessages] = useImmer([]);
  const [newMessage, setNewMessage] = useState('');

  const isLoading = messages.length && messages[messages.length - 1].loading;

  async function submitNewMessage() {
    const trimmedMessage = newMessage.trim();
    if (!trimmedMessage || isLoading) return;

    setMessages(draft => [...draft,
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

      // Simulate the streaming behavior
      let currentIndex = -1;
      const chunkSize = 1; // You can adjust this based on how fast you want the stream
      const totalLength = answer.length;

      const interval = setInterval(() => {
        // Append a chunk to the message content
        setMessages(draft => {
          draft[draft.length - 1].content += answer.slice(currentIndex, currentIndex + chunkSize);
        });

        currentIndex += chunkSize;
        
        if (currentIndex >= totalLength) {
          clearInterval(interval);
          setMessages(draft => {
            draft[draft.length - 1].loading = false;
          });
        }
      }, 20);  // Adjust the interval to control the speed of the "stream"


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