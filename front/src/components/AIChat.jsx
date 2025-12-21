const AIChat = ({ messages }) => {
  const getMessageStyle = (type) => {
    switch (type) {
      case "system":
        return "chat-bubble-info";
      case "ai":
      case "response":
        return "chat-bubble-primary";
      case "query":
        return "chat-bubble-secondary";
      case "success":
        return "chat-bubble-success";
      case "error":
        return "chat-bubble-error";
      default:
        return "chat-bubble-neutral";
    }
  };

  const getMessageIcon = (type) => {
    switch (type) {
      case "system":
        return "⚙️";
      case "ai":
      case "response":
        return "🤖";
      case "query":
        return "❓";
      case "success":
        return "✅";
      case "error":
        return "❌";
      default:
        return "💬";
    }
  };

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h3 className="card-title text-primary">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
          Assistant IA Gemini
        </h3>
        <div className="divider mt-0"></div>
        <div className="max-h-96 overflow-y-auto space-y-3">
          {messages.length === 0 ? (
            <div className="text-center text-base-content/50 py-8">
              <p>Aucun message pour le moment</p>
              <p className="text-sm mt-2">Cliquez sur "Démarrer l'IA" pour commencer</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`alert ${getMessageStyle(message.type)} shadow-md`}
              >
                <div className="flex flex-col w-full">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{getMessageIcon(message.type)}</span>
                    <div className="flex-1">
                      <p className="font-medium whitespace-pre-wrap">{message.content}</p>
                      {message.action && (
                        <p className="text-sm opacity-70 mt-1">Action: {message.action}</p>
                      )}
                    </div>
                    <time className="text-xs opacity-50">{message.time}</time>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default AIChat;
