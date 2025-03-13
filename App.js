import React, { useEffect, useState } from "react";
import io from "socket.io-client";

const socket = io("http://localhost:5000");

function App() {
  const [username, setUsername] = useState("");
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [file, setFile] = useState(null);

  useEffect(() => {
    socket.on("message", (data) => {
      setMessages((prev) => [...prev, data]);
    });
  }, []);

  const sendMessage = () => {
    if (message || file) {
      const reader = new FileReader();
      if (file) {
        reader.readAsDataURL(file);
        reader.onload = () => {
          socket.send({ user: username, text: message, file: reader.result });
          setFile(null);
          setMessage("");
        };
      } else {
        socket.send({ user: username, text: message, file: null });
        setMessage("");
      }
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "600px", margin: "auto" }}>
      <h2>Мессенджер</h2>
      {!username && (
        <input
          type="text"
          placeholder="Введите имя"
          onChange={(e) => setUsername(e.target.value)}
        />
      )}
      <div>
        {messages.map((msg, index) => (
          <div key={index} style={{ border: "1px solid #ccc", padding: "10px", marginBottom: "10px" }}>
            <strong>{msg.user}:</strong> {msg.text}
            {msg.file && (
              msg.file.startsWith("data:image") ? (
                <img src={msg.file} alt="file" style={{ maxWidth: "100%", cursor: "pointer" }} onClick={() => window.open(msg.file, "_blank")} />
              ) : (
                <video controls width="100%"><source src={msg.file} type="video/mp4" /></video>
              )
            )}
          </div>
        ))}
      </div>
      <input type="text" placeholder="Введите сообщение..." value={message} onChange={(e) => setMessage(e.target.value)} />
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={sendMessage}>Отправить</button>
    </div>
  );
}

export default App;
