import React from 'react';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

const CodeViewer = ({ fileA, fileB, contentA, contentB, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white w-full max-w-6xl h-[90vh] rounded-lg shadow-2xl flex flex-col overflow-hidden">
        
        {/* Header */}
        <div className="bg-gray-100 px-6 py-4 border-b flex justify-between items-center">
          <h3 className="text-xl font-bold text-gray-800">Clone Comparison</h3>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-red-500 text-2xl font-bold leading-none"
          >
            &times;
          </button>
        </div>

        {/* Comparison Area */}
        <div className="flex-1 flex overflow-hidden">
          
          {/* Left File */}
          <div className="flex-1 border-r flex flex-col">
            <div className="bg-gray-50 p-2 border-b font-semibold text-center text-blue-700">
              {fileA}
            </div>
            {/* Added text-left class to container and textAlign: 'left' to customStyle */}
            <div className="flex-1 overflow-auto bg-gray-50 text-sm text-left">
              <SyntaxHighlighter 
                language="cpp" 
                style={docco} 
                showLineNumbers={true}
                customStyle={{ 
                  margin: 0, 
                  padding: '1.5rem', 
                  minHeight: '100%', 
                  textAlign: 'left' // <--- Forces left alignment
                }}
              >
                {contentA || "// Loading content..."}
              </SyntaxHighlighter>
            </div>
          </div>

          {/* Right File */}
          <div className="flex-1 flex flex-col">
            <div className="bg-gray-50 p-2 border-b font-semibold text-center text-red-700">
              {fileB}
            </div>
            {/* Added text-left class to container and textAlign: 'left' to customStyle */}
            <div className="flex-1 overflow-auto bg-gray-50 text-sm text-left">
              <SyntaxHighlighter 
                language="cpp" 
                style={docco} 
                showLineNumbers={true}
                customStyle={{ 
                  margin: 0, 
                  padding: '1.5rem', 
                  minHeight: '100%', 
                  textAlign: 'left' // <--- Forces left alignment
                }}
              >
                {contentB || "// Loading content..."}
              </SyntaxHighlighter>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="bg-gray-100 px-6 py-3 border-t text-right">
          <button 
            onClick={onClose}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Close Viewer
          </button>
        </div>
      </div>
    </div>
  );
};

export default CodeViewer;