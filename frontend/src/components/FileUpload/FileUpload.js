// src/components/FileUpload/FileUpload.js
import React, { useState } from 'react';

const FileUpload = () => { // lastUploadDate больше не нужен
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(''); // 'idle', 'uploading', 'success', 'error'

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') {
      setSelectedFile(file);
      setUploadStatus('idle');
    } else {
      alert('Пожалуйста, выберите файл в формате .xlsx');
      event.target.value = null;
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Пожалуйста, выберите файл для загрузки.');
      return;
    }

    setUploadStatus('uploading');
    // setUploadStatus('idle'); // Сброс, так как API нет

    try {
      console.log("Отправка файла на бэкенд:", selectedFile, new Date().toISOString());
      setUploadStatus('success');
      setTimeout(() => setUploadStatus('idle'), 3000);

    } catch (error) {
      console.error("Ошибка при загрузке файла:", error);
      setUploadStatus('error');
      setTimeout(() => setUploadStatus('idle'), 3000);
    }
  };

  return (
    <div className="file-upload-container">
      <div className="file-upload-section">
        <h3>Загрузка данных из Excel</h3>
        <div className="file-input-wrapper">
          <input
            type="file"
            id="excel-file"
            accept=".xlsx"
            onChange={handleFileChange}
          />
          <label htmlFor="excel-file">Выберите файл .xlsx</label>
        </div>
        <button onClick={handleUpload} disabled={!selectedFile || uploadStatus === 'uploading'}>
          {uploadStatus === 'uploading' ? 'Загрузка...' : 'Загрузить'}
        </button>

        {uploadStatus === 'success' && <p className="status success">Файл успешно загружен!</p>}
        {uploadStatus === 'error' && <p className="status error">Ошибка загрузки файла.</p>}

        {/* УДАЛЕНО: Отображение даты последней загрузки */}
        {/* {lastUploadDate && (
          <p className="last-upload-date">
            <strong>Последняя загрузка:</strong> {lastUploadDate}
          </p>
        )}
        {!lastUploadDate && (
          <p className="last-upload-date">
            <em>Файлы ещё не загружались.</em>
          </p>
        )} */}
      </div>
    </div>
  );
};

export default FileUpload;