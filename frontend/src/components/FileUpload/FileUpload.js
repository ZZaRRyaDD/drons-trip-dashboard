// src/components/FileUpload/FileUpload.js
import React, { useState } from 'react';
import './FileUpload.css'; // Убедитесь, что стили лежат рядом

const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(''); // '', 'uploading', 'success', 'error'
  const [uploadMessage, setUploadMessage] = useState(''); // Для отображения сообщений пользователю

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    // Проверяем тип файла. XLSX имеет MIME-тип application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
    // Также можно проверить расширение, если MIME не всегда корректен
    if (file && (file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || file.name.endsWith('.xlsx'))) {
      setSelectedFile(file);
      setUploadStatus('');
      setUploadMessage('');
    } else {
      alert('Пожалуйста, выберите файл в формате .xlsx');
      event.target.value = null; // Сбросить выбор файла в инпуте
      // Также сбросим состояние, если файл был выбран ранее
      setSelectedFile(null);
      setUploadStatus('');
      setUploadMessage('');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Пожалуйста, сначала выберите файл.');
      return;
    }

    setUploadStatus('uploading');
    setUploadMessage('Загрузка файла...');
    
    // Определяем URL сервера в зависимости от среды
    let serverUrl = "localhost:8000"; // По умолчанию для разработки
    if (process.env.NODE_ENV === "production") {
      serverUrl = "193.168.46.16"; // IP production сервера
    }
    const uploadUrl = `http://${serverUrl}/api/flights/upload`; // Новый эндпоинт

    // Создаём объект FormData для отправки файла
    const formData = new FormData();
    formData.append('file', selectedFile); // Добавляем файл в форму под ключом 'file'

    try {
      console.log(`Отправка файла ${selectedFile.name} на ${uploadUrl}`);
      
      const response = await fetch(uploadUrl, {
        method: 'POST', // Метод POST для загрузки файлов
        // Не устанавливаем Content-Type вручную! Браузер сам установит правильный заголовок
        // с boundary для multipart/form-data, когда используется FormData.
        // headers: {
        //   'Content-Type': 'multipart/form-data', // <-- НЕ НУЖНО
        // },
        body: formData, // Тело запроса - наш FormData объект
      });

      console.log('Ответ от сервера загрузки:', response);

      if (response.ok) {
        // Файл успешно загружен
        const result = await response.json(); // Предполагаем, что сервер возвращает JSON
        console.log('Успешная загрузка:', result);
        setUploadStatus('success');
        // Сообщение может прийти от сервера, например, result.message
        setUploadMessage(result.message || `Файл "${selectedFile.name}" успешно загружен.`);
        
        // Сбросить выбор файла после успешной загрузки
        setSelectedFile(null);
        // Сбросить значение инпута файла, чтобы можно было выбрать тот же файл снова
        const fileInput = document.getElementById('excel-file');
        if (fileInput) {
            fileInput.value = '';
        }
        
      } else {
        // Сервер вернул ошибку (например, 4xx, 5xx)
        console.error(`Ошибка загрузки: ${response.status} ${response.statusText}`);
        setUploadStatus('error');
        // Попробуем получить сообщение об ошибке от сервера
        let errorMessage = `Ошибка загрузки файла: ${response.status} ${response.statusText}`;
        try {
            const errorResult = await response.json();
            if (errorResult && errorResult.detail) {
                errorMessage = `Ошибка: ${errorResult.detail}`;
            } else if(errorResult && errorResult.message) {
                errorMessage = `Ошибка: ${errorResult.message}`;
            }
        } catch (e) {
            // Если не удалось распарсить JSON, оставляем дефолтное сообщение
            console.warn('Не удалось получить детали ошибки от сервера.', e);
        }
        setUploadMessage(errorMessage);
      }
    } catch (error) {
      // Ошибка сети или другая JS ошибка
      console.error('Ошибка сети или обработки запроса:', error);
      setUploadStatus('error');
      setUploadMessage(`Ошибка при загрузке файла: ${error.message || 'Неизвестная ошибка'}`);
    } finally {
      // Можно убрать статус "uploading" через некоторое время, если нужно
      // setTimeout(() => {
      //   if (uploadStatus === 'success' || uploadStatus === 'error') {
      //     setUploadStatus('');
      //   }
      // }, 3000);
    }
  };

  return (
    <div className="file-upload-container">
      <div className="file-upload-section">
        <h3>Загрузка данных из Excel</h3>
        <div className="file-input-wrapper">
          {/* Input для выбора файла */}
          <input
            type="file"
            id="excel-file"
            accept=".xlsx" // Ограничиваем выбор только .xlsx файлами
            onChange={handleFileChange}
          />
          {/* Кастомная метка для input'а */}
          <label htmlFor="excel-file">
            {selectedFile ? selectedFile.name : 'Выберите файл .xlsx'}
          </label>
        </div>
        
        {/* Кнопка загрузки */}
        <button
          onClick={handleUpload}
          disabled={!selectedFile || uploadStatus === 'uploading'} // Отключена, если файл не выбран или идёт загрузка
          className="upload-button"
        >
          {uploadStatus === 'uploading' ? 'Загрузка...' : 'Загрузить'}
        </button>

        {/* Отображение статуса и сообщений */}
        {uploadMessage && (
          <p className={`status ${uploadStatus}`}>
            {uploadMessage}
          </p>
        )}
      </div>
    </div>
  );
};

export default FileUpload;