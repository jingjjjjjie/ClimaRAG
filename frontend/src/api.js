const BASE_URL = import.meta.env.VITE_API_URL;

async function createChat() {
  const res = await fetch(BASE_URL + '/api/v1/chats', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  const data = await res.json();
  if (!res.ok) {
    return Promise.reject({ status: res.status, data });
  }
  return data;
}

async function sendChatMessage(chatId, text) {
  try {
    const res = await fetch(BASE_URL + `/api/v1/chats/${chatId}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    if (!res.ok) {
      // Reject with an error object containing the status and response data
      return Promise.reject({ status: res.status, data: await res.json() });
    }

    // Parse the response body as JSON
    const responseBody = await res.json();
    return responseBody;
  } catch (error) {
    // Handle network or other unexpected errors
    return Promise.reject({ status: 'network_error', data: error });
  }
}


export default {
  createChat, sendChatMessage
};