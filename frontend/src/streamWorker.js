self.onmessage = function(event) {
  const { answer, chunkSize } = event.data;
  let currentIndex = 0;
  const totalLength = answer.length;

  function stream() {
    if (currentIndex < totalLength) {
      const chunk = answer.slice(currentIndex, currentIndex + chunkSize);
      currentIndex += chunkSize;
      self.postMessage({ chunk, done: false });
      setTimeout(stream, 50); // Adjust delay as needed
    } else {
      self.postMessage({ done: true });
    }
  }

  stream();
}; 