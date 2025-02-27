import streamlit as st
import pandas as pd
from io import BytesIO

def process_codes(df):
    # Получаем имя первого столбца
    col_name = df.columns[0]
    
    # Применяем преобразования
    df[col_name] = (
        df[col_name]
        .astype(str)
        .str.replace(r'\s+', '', regex=True)          # Удаление пробелов
        .str.replace(r'(?i)из', '', regex=True)       # Удаление "Из" и "из" (регистронезависимо)
        .str[:6]                                      # Обрезка после 6 символов
    )
    return df

# Интерфейс
st.title("Обработка кодов")
uploaded_file = st.file_uploader("Программа проводит последовательно вот такие операции с этими кодами: 1)	Убрать пробелы везде в ячейках; 2)	Убрать «Из» и «из» из ячеек; 3)	Убрать все символы стоящие после 6 знаков. Для продолжения загрузите XLSX файл с одним столбцом, содержащим коды", type="xlsx")

if uploaded_file:
    try:
        # Чтение файла
        df = pd.read_excel(uploaded_file)
        
        # Проверка количества столбцов
        if len(df.columns) != 1:
            st.error("Файл должен содержать только один столбец!")
            st.stop()
            
        # Обработка данных
        processed_df = process_codes(df)
        
        # Создание файла для скачивания
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            processed_df.to_excel(writer, index=False)
            
        # Показ результатов
        st.success("Обработка завершена!")
        
        # Кнопка скачивания
        st.download_button(
            label="Скачать обработанный файл",
            data=output.getvalue(),
            file_name="processed_codes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Превью данных
        st.subheader("Предпросмотр обработанных данных")
        st.dataframe(processed_df.head(20))
        
    except Exception as e:
        st.error(f"Ошибка обработки файла: {str(e)}")