import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { Send, Bot, User, FileText, AlertCircle, Loader } from "lucide-react";

const API_BASE_URL =
  process.env.REACT_APP_API_URL ||
  "https://edurag-retrieval-augmented-educational.onrender.com";

export const ChatInterface = ({ systemStatus, files }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: "user",
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: inputMessage,
      });

      const botMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: response.data.answer,
        sources: response.data.sources || [],
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      setError(error.response?.data?.detail || "Error sending message");

      const errorMessage = {
        id: Date.now() + 1,
        type: "error",
        content: error.response?.data?.detail || "Error sending message",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  const exampleQuestions = [
    "What is Parkinson's disease?",
    "How is Parkinson's disease detected?",
    "What are the symptoms of Parkinson's?",
    "What machine learning methods are used for detection?",
  ];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border h-[600px] flex flex-col">
        {/* Chat Header */}
        <div className="p-4 border-b bg-gray-50 rounded-t-lg">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Chat with Your Documents
            </h2>
            <div className="flex items-center space-x-2">
              {systemStatus.embeddingsReady ? (
                <div className="flex items-center space-x-1 text-green-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm">Ready</span>
                </div>
              ) : (
                <div className="flex items-center space-x-1 text-yellow-600">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span className="text-sm">Upload documents first</span>
                </div>
              )}
              <button
                onClick={clearChat}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Clear
              </button>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-8">
              <Bot className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Start a conversation with your documents
              </h3>
              <p className="text-gray-500 mb-6">
                Ask questions about the content in your uploaded PDF files
              </p>

              {systemStatus.embeddingsReady && (
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">Try asking:</p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {exampleQuestions.map((question, index) => (
                      <button
                        key={index}
                        onClick={() => setInputMessage(question)}
                        className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.type === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.type === "user"
                      ? "bg-blue-600 text-white"
                      : message.type === "error"
                      ? "bg-red-100 text-red-800 border border-red-200"
                      : "bg-gray-100 text-gray-900"
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {message.type === "user" ? (
                      <User className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    ) : message.type === "error" ? (
                      <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    ) : (
                      <Bot className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <ReactMarkdown className="prose prose-sm max-w-none">
                        {message.content}
                      </ReactMarkdown>

                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <p className="text-xs font-medium text-gray-600 mb-2">
                            Sources:
                          </p>
                          <div className="space-y-1">
                            {message.sources.map((source, index) => (
                              <div
                                key={index}
                                className="text-xs text-gray-600"
                              >
                                <div className="flex items-center space-x-1">
                                  <FileText className="h-3 w-3" />
                                  <span className="font-medium">
                                    {source.file}
                                  </span>
                                </div>
                                <p className="text-gray-500 mt-1">
                                  {source.chunk}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <Loader className="h-4 w-4 animate-spin" />
                  <span className="text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t bg-gray-50 rounded-b-lg">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                systemStatus.embeddingsReady
                  ? "Ask a question about your documents..."
                  : "Upload documents first to start chatting..."
              }
              disabled={!systemStatus.embeddingsReady || isLoading}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <button
              onClick={sendMessage}
              disabled={
                !inputMessage.trim() ||
                !systemStatus.embeddingsReady ||
                isLoading
              }
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>

          {error && (
            <div className="mt-2 p-2 bg-red-100 text-red-800 rounded text-sm">
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
