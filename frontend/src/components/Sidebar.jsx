import { useState } from 'react';
import api from '@/api';
import { FaEdit } from 'react-icons/fa';

function Sidebar({ startNewChat, conversations, fetchMessages }) {
  const [open, setOpen] = useState(true);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [chatNames, setChatNames] = useState({});
  const [isEditing, setIsEditing] = useState(false);
  const [currentChatId, setCurrentChatId] = useState(null);

  const handleConversationClick = async (sessionId) => {
    setSelectedConversation(sessionId);
    await fetchMessages(sessionId);
  };

  const handleNewChat = () => {
    setSelectedConversation(null);
    startNewChat();
  };

  const handleEditChatName = (sessionId) => {
    setIsEditing(true);
    setCurrentChatId(sessionId);
  };

  const handleSaveChatName = async (sessionId) => {
    const newChatName = chatNames[sessionId] || '';
    console.log(newChatName);
    try {
      const updatedSession = await api.updateChatName(sessionId, newChatName);
      setChatNames(prev => ({ ...prev, [sessionId]: updatedSession.chat_name }));
    } catch (error) {
      console.error("Error updating chat name:", error);
    }
    setIsEditing(false);
    setCurrentChatId(null);
  };

  return (
    <div className="flex">
      <div className={`${open ? "w-72" : "w-20 "} bg-dark-purple h-screen p-5 pt-8 relative duration-300`}>
        <img
          src="./src/assets/images/control.png"
          className={`absolute cursor-pointer -right-3 top-9 w-7 border-dark-purple border-2 rounded-full ${!open && "rotate-180"}`}
          onClick={() => setOpen(!open)}
        />
        <div className="flex gap-x-4 items-center">
          <img src="./src/assets/images/logo.png" className={`cursor-pointer duration-500 ${open && "rotate-[360deg]"}`} />
          <h1 className={`text-white origin-left font-medium text-xl duration-200 ${!open && "scale-0"}`}>Tools</h1>
        </div>
        <ul className="pt-6 overflow-y-auto max-h-[calc(100vh-100px)]">
          <li className="flex rounded-md p-2 cursor-pointer hover:bg-light-purple text-white text-sm items-center gap-x-4" onClick={handleNewChat}>
            <img src={`./src/assets/images/Chat.png`} />
            <span className={`${!open && "hidden"} origin-left duration-200`}>New Chat</span>
          </li>
          <h2 className={`${!open && "hidden"} text-white mt-4`}>Conversation History</h2>
          {conversations.map((conv, index) => (
            <li
              key={index}
              className={`flex rounded-md p-2 cursor-pointer text-white text-sm items-center gap-x-4 ${selectedConversation === conv.id ? 'bg-light-purple' : 'hover:bg-light-purple'}`}
              onClick={() => handleConversationClick(conv.id)}
            >
              {isEditing && currentChatId === conv.id ? (
                <input
                  type="text"
                  value={chatNames[conv.id] || ''}
                  onChange={(e) => {
                    const value = e.target.value;
                    setChatNames(prev => ({ ...prev, [conv.id]: value }));
                  }}
                  onBlur={() => handleSaveChatName(conv.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleSaveChatName(conv.id);
                    }
                  }}
                  className="bg-transparent text-white border-b border-white"
                />
              ) : (
                <span className={`${!open && "hidden"} origin-left duration-200 flex items-center`}>
                  {chatNames[conv.id] || conv.chat_name}
                  <FaEdit 
                    className="ml-2 cursor-pointer" 
                    onClick={() => handleEditChatName(conv.id)}
                  />
                </span>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Sidebar;
