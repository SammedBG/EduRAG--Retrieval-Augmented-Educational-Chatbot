import React from 'react';
import { CheckCircle, XCircle, Clock, FileText } from 'lucide-react';

export const StatusBar = ({ systemStatus, fileCount, isProcessing }) => {
  return (
    <div className="bg-white border-b shadow-sm">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <FileText className="h-4 w-4 text-gray-500" />
              <span className="text-gray-600">
                {fileCount} document{fileCount !== 1 ? 's' : ''} uploaded
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              {systemStatus.embeddingsReady ? (
                <>
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-green-600">Ready for queries</span>
                </>
              ) : (
                <>
                  <XCircle className="h-4 w-4 text-yellow-500" />
                  <span className="text-yellow-600">Upload documents to start</span>
                </>
              )}
            </div>
          </div>

          {isProcessing && (
            <div className="flex items-center space-x-2 text-blue-600">
              <Clock className="h-4 w-4 animate-spin" />
              <span>Processing documents...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
